import React, {Component} from 'react';
import Search from "../components/search/Search";
import Webpage from "../components/webpage/Webpage";
import './App.css';

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

    // Source: https://github.com/mdn/dom-examples/blob/master/streams/simple-pump/index.html
    handleClick = () => {
        if (this.state.isSingleClick) {
            this.startSingleCounter();
        } else {
            this.startHybridCounter();
        }
        fetch(`http://192.168.1.37:8080/${this.state.address}`)
            .then(response => response.body)
            .then(response => {
                if (this.state.isSingleClick) {
                    this.stopSingleCounter();
                } else {
                    this.stopHybridCounter();
                }
                let outerThis = this;
                const reader = response.getReader();
                return new ReadableStream({
                    async start(controller) {
                        let length = 0;
                        while (true) {
                            const {done, value} = await reader.read();
                            if (done) break;
                            controller.enqueue(value);
                            length += value.length;
                            if (outerThis.state.isSingleClick) {
                                outerThis.setState({
                                    hybridBytes: length
                                });
                            } else {
                                outerThis.setState({
                                    singleBytes: length
                                });
                            }
                            console.log(length);
                        }
                        controller.close();
                        reader.releaseLock();
                    }
                })
            })
            .then(response => new Response(response))
            .then(response => response.blob())
            .then(blob => URL.createObjectURL(blob))
            .then(url => {
                this.setState({
                    url: url
                });
            })
            .catch(error => console.log(error))
    };

    startSingleCounter = () => {
        this.setState({
            singleCounter: 0,
            singleBytes: 0
        });
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
        this.setState({
            hybridCounter: 0,
            hybridBytes: 0
        });
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