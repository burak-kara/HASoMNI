import React, {Component} from 'react';
import './App.css';
import Search from "../components/search/Search";
import Webpage from "../components/webpage/Webpage";

export default class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            address: "",
            url: "",
            isSingleClick: true,
            singleCounter: 0,
            hybridCounter: 0,
            singleBytes: 0,
            hybridBytes: 0
        };
    }

    render() {
        return (
            <div className="App" style={{height: window.innerHeight}}>
                <Search handleClick={this.handleClick} handleChange={this.handleChange}/>
                <Webpage
                    url={this.state.url}
                    singleCounter={this.state.singleCounter}
                    singleBytes={this.state.singleBytes}
                    hybridCounter={this.state.hybridCounter}
                    hybridBytes={this.state.hybridBytes}
                />
            </div>
        );
    }

    handleChange = (event) => {
        this.setState({[event.target.name]: event.target.value})
    };

    // http://clips.vorwaerts-gmbh.de/VfE_html5.mp4

    // Source: https://github.com/mdn/dom-examples/blob/master/streams/simple-pump/index.html
    handleClick = () => {
        if (this.state.isSingleClick) {
            this.startSingleCounter();
        } else {
            this.startHybridCounter();
        }
        fetch(`http://192.168.1.33:8080/${this.state.address}`)
            .then(response => response.body)
            .then(response => {
                if (this.state.isSingleClick) {
                    this.stopSingleCounter();
                } else {
                    this.stopHybridCounter();
                }
                const reader = response.getReader();
                return new ReadableStream({
                    async start(controller) {
                        let length = 0;
                        while (true) {
                            const {done, value} = await reader.read();
                            if (done) break;
                            controller.enqueue(value);
                            length += value.length;
                        }
                        controller.close();
                        reader.releaseLock();
                        console.log(length);

                    }
                }.bind(this))
            })
            .then(response => new Response(response))
            .then(response => response.blob())
            .then(blob => URL.createObjectURL(blob))
            .then(url => {
                this.setState({
                    url: url
                });
                console.log(url);
            })
            .catch(error => console.log(error))
    };

    startSingleCounter = () => {
        this.timerSingle = setInterval(() => {
            this.setState({
                singleCounter: ++this.state.singleCounter
            })
        }, 1000);
    };

    stopSingleCounter = () => {
        clearInterval(this.timerSingle);
        this.setState({
            isSingleClick: false
        })
    };

    startHybridCounter = () => {
        this.timerHybrid = setInterval(() => {
            this.setState({
                hybridCounter: ++this.state.hybridCounter
            })
        }, 1000);
    };

    stopHybridCounter = () => {
        clearInterval(this.timerHybrid);
        this.setState({
            isSingleClick: true
        })
    };
}