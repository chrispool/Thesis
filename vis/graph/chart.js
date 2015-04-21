$(function () {
    $('#container').highcharts({
        title: {
            text: 'Event Chart',
            x: -20 //center
        },
        /*subtitle: {
            text: 'Source: WorldClimate.com',
            x: -20
        },*/
        xAxis: {
            title: {
                text: 'time'
            },
        },
        yAxis: {
            title: {
                text: 'n tweets'
            },
            plotLines: [{
                value: 0,
                width: 1,
                color: '#808080'
            }]
        },
        tooltip: {
            formatter: function () {
                return this.point.myData;
            }
        },

    series: [{
        name: 'Foo',
        data: [{
            y: 3,
            myData: 'Insert tweet text here',
        }, {
            y: 7,
            myData: 'Insert tweet text here'
        }, {
            y: 1,
            myData: 'Insert tweet text here'
        }, {
            y: 8,
            myData: 'Insert tweet text here'
        }, {
            y: 9,
            myData: 'Insert tweet text here'
        }, {
            y: 10,
            myData: 'Insert tweet text here'
        }, {
            y: 5,
            myData: 'Insert tweet text here'
        }, {
            y: 12,
            myData: 'Insert tweet text here'
        }, {
            y: 13,
            myData: 'Insert tweet text here'
        }, {
            y: 15,
            myData: 'Insert tweet text here'
        }, {
            y: 9,
            myData: 'Insert tweet text here'
        }, {
            y: 21,
            myData: 'Insert tweet text here'
        }, {
            y: 23,
            myData: 'Insert tweet text here'
        }]
    }]
    });
});