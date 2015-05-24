package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"github.com/pebbe/textcat"
	"github.com/pebbe/util"
	"html"
	"io"
	"log"
	"os"
	"regexp"
	"strings"
	"time"
)

type stTweet struct {
	Coordinates      stCoor
	Created_at       string
	Entities         stEntities
	Id_str           string
	Place            stPlace
	Retweeted_status stRetweet
	Text             string
	User             stUser
	Lang             string
}

type stRetweet struct {
	Id_str string
	User   stUser
}

type stUser struct {
	Id_str      string
	Description string
	Lang        string
	Location    string
	Name        string
	Screen_name string
}

type stCoor struct {
	Coordinates []float64
}

type stEntities struct {
	Hashtags      []stHashtag
	Media         []stUrl
	Urls          []stUrl
	User_mentions []stMention
}

type stHashtag struct {
	Text string
}

type stUrl struct {
	Expanded_url string
	Url          string
}

type stMention struct {
	Screen_name string
}

type stPlace struct {
	Country   string
	Full_name string
}

var (
	opt_k  = flag.Bool("k", false, "keep going")
	opt_i  = flag.Bool("i", false, "ignore errors")
	opt_e  = flag.Bool("e", false, "expand URLs")
	reWord = regexp.MustCompile("(" +
		// url
		"[hH][tT][tT][pP][sS]?:([-A-Za-z0-9\\._~:/?#\\[\\]@!$&'\\(\\)\\*\\+,;=]|%[0-9a-fA-f][0-9a-fA-f])*" +
		"|" +
		// hashtag
		"#[\\p{L}0-9]+" +
		"|" +
		// mention
		"@[a-zA-Z0-9_]+" +
		"|" +
		// word
		"\\p{L}([-']\\p{L}|\\p{L})+" +
		")")
	printErrors = true
	keepGoing   = false
	missingID   = errors.New("Missing 'id_str' in JSON object")
	usage       = `
Usage: %s [-e|-i|-k] field ...

Reads twitter data as JSON objects (one per line) from standard input,
extracts parts, and exports to tab-delimited output.

Example usage:

    gunzip -c twitterdata.gz | %s -i user text

Options:

    -e : expand URLs
    -i : ignore errors
    -k : print errors, but keep going

Fields:

    text                the tweet
    words               the tweet with spaces inserted between words and punctuation
    id                  the tweet id
    lang                the tweet language, determined by twitter, available since 20 Feb 2013,
                   after 9 May 2014 this will always be 'nl', for data in /net/corpora/twitter2
    date                the date and time the tweet was created
    textcat             the language guessed by textcat
    textcat10           like 'textcat', but also for shorter tweet (minimum length = 10)
    coordinates         the coordinates of the tweet
    place               the place of the tweet
    hashtags            #tags in the tweet
    mentions            @mentions in the tweet
    urls                urls in the tweet
    user                the screen name of the user
    user.id             the id of the user
    user.name           the real name of the user
    user.description    the description of the user
    user.lang           the language preference of the user
    user.location       the location of the user
    rt.id               for retweet, the id of the original tweet
    rt.user             for retweet, the screen name of the original user
    rt.user.id          for retweet, the id of the original user
    rt.user.name        for retweet, the real name of the original user
    rt.user.description for retweet, the description of the original user
    rt.user.lang        for retweet, the language preference of the original user
    rt.user.location    for retweet, the location of the original user

`
)

func main() {
	flag.Parse()
	if flag.NArg() == 0 || util.IsTerminal(os.Stdin) {
		fmt.Fprintf(os.Stderr, usage, os.Args[0], os.Args[0])
		return
	}
	if *opt_i && *opt_k {
		log.Fatalln("Can't use both options -i and -k")
	}
	if *opt_i {
		keepGoing = true
		printErrors = false
	}
	if *opt_k {
		keepGoing = true
	}

	location, err := time.LoadLocation("Europe/Amsterdam")
	util.CheckErr(err)

	tc1 := textcat.NewTextCat()
	tc1.EnableAllUtf8Languages()

	tc2 := textcat.NewTextCat()
	tc2.EnableAllUtf8Languages()
	tc2.SetMinDocSize(10)

	lineno := int64(0)
	r := util.NewReaderSize(os.Stdin, 50000)
	for {
		var tweet stTweet
		var err error
		var prefix bool

		line, err := r.ReadLine()
		if err == io.EOF {
			break
		}
		util.CheckErr(err)
		lineno += 1

		err = json.Unmarshal(line, &tweet)
		if err == nil {
			if len(tweet.Id_str) == 0 {
				err = missingID
			}
		}
		if err != nil {
			if printErrors {
				log.Printf("%v\n\tin line %v: %v\n", err.Error(), lineno, string(line))
			}
			if keepGoing {
				continue
			} else {
				break
			}
		}

		for _, field := range flag.Args() {
			if prefix {
				fmt.Print("\t")
			} else {
				prefix = true
			}
			switch field {
			case "id":
				fmt.Print(tweet.Id_str)
			case "text":
				text := sanitize(tweet.Text)
				if *opt_e {
					text = expand_urls(text, &tweet)
				}
				fmt.Print(text)
			case "lang":
				fmt.Print(tweet.Lang)
			case "words":
				text := strings.Join(strings.Fields(reWord.ReplaceAllString(html.UnescapeString(tweet.Text), " $1 ")), " ")
				if *opt_e {
					text = expand_urls(text, &tweet)
				}
				fmt.Print(text)
			case "textcat", "textcat10":
				words := strings.Fields(reWord.ReplaceAllString(html.UnescapeString(tweet.Text), " $1 "))
				w := []string{}
				for _, ww := range words {
					if !(ww == "RT" ||
						strings.HasPrefix(ww, "@") ||
						strings.HasPrefix(ww, "#") ||
						strings.HasPrefix(ww, "http:") ||
						strings.HasPrefix(ww, "https:")) {
						w = append(w, ww)
					}
				}
				tc := tc1
				if field == "textcat10" {
					tc = tc2
				}
				language, err := tc.Classify(strings.Join(w, " "))
				if err != nil {
					fmt.Print("error:" + err.Error())
				} else {
					fmt.Print(strings.Replace(strings.Join(language, " "), ".utf8", "", -1))
				}
			case "date":
				t, err := time.Parse(time.RubyDate, tweet.Created_at)
				if err != nil {
					if printErrors {
						log.Println("Error in decoding 'created_at': " + err.Error())
					}
				} else {
					t = t.In(location)
					zone, _ := t.Zone()
					fmt.Printf("%04d-%02d-%02d %02d:%02d:%02d %s %s",
						t.Year(), t.Month(), t.Day(),
						t.Hour(), t.Minute(), t.Second(),
						zone, t.Weekday().String()[:3])
				}
			case "hashtags":
				t := make([]string, len(tweet.Entities.Hashtags))
				for i, h := range tweet.Entities.Hashtags {
					t[i] = "#" + h.Text
				}
				fmt.Print(strings.Join(t, " "))
			case "mentions":
				t := make([]string, len(tweet.Entities.User_mentions))
				for i, m := range tweet.Entities.User_mentions {
					t[i] = "@" + m.Screen_name
				}
				fmt.Print(strings.Join(t, " "))
			case "urls":
				t := make([]string, len(tweet.Entities.Urls))
				for i, u := range tweet.Entities.Urls {
					if *opt_e && len(u.Expanded_url) != 0 {
						t[i] = u.Expanded_url
					} else {
						t[i] = u.Url
					}
				}
				fmt.Print(strings.Join(t, " "))
			case "user":
				fmt.Print(tweet.User.Screen_name)
			case "user.name":
				fmt.Print(sanitize(tweet.User.Name))
			case "user.id":
				fmt.Print(tweet.User.Id_str)
			case "user.description":
				fmt.Print(sanitize(tweet.User.Description))
			case "user.lang":
				fmt.Print(tweet.User.Lang)
			case "user.location":
				fmt.Print(sanitize(tweet.User.Location))
			case "coordinates":
				if coo := tweet.Coordinates.Coordinates; len(coo) == 2 {
					fmt.Printf("%v %v", coo[0], coo[1])
				}
			case "place":
				i1 := tweet.Place.Full_name
				i2 := tweet.Place.Country
				if len(i1) > 0 && len(i2) > 0 {
					fmt.Printf("%s, %s", sanitize(i1), sanitize(i2))
				}
			case "rt.id":
				fmt.Print(tweet.Retweeted_status.Id_str)
			case "rt.user":
				fmt.Print(tweet.Retweeted_status.User.Screen_name)
			case "rt.user.name":
				fmt.Print(sanitize(tweet.Retweeted_status.User.Name))
			case "rt.user.id":
				fmt.Print(tweet.Retweeted_status.User.Id_str)
			case "rt.user.description":
				fmt.Print(sanitize(tweet.Retweeted_status.User.Description))
			case "rt.user.lang":
				fmt.Print(tweet.Retweeted_status.User.Lang)
			case "rt.user.location":
				fmt.Print(sanitize(tweet.Retweeted_status.User.Location))
			default:
				log.Fatalln("Unknown field: " + field)
			}
		}
		fmt.Print("\n")
	}
}

func sanitize(s string) string {
	return strings.Join(strings.Fields(html.UnescapeString(s)), " ")
}

func expand_urls(text string, tweet *stTweet) string {
	for _, url := range tweet.Entities.Urls {
		if len(url.Expanded_url) != 0 {
			text = strings.Replace(text, url.Url, url.Expanded_url, -1)
		}
	}
	for _, url := range tweet.Entities.Media {
		if len(url.Expanded_url) != 0 {
			text = strings.Replace(text, url.Url, url.Expanded_url, -1)
		}
	}
	return text
}
