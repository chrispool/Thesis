import sys

def main():
    tweets = [] 
    for line in sys.stdin:
        elements = line.strip().split('\t')
        if elements[1] != '' :
        tweets.append(elements)
        print('\t'.join(elements))

main()