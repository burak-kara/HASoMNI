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
            clickCount: 0,
            primaryCounter: 0,
            secondaryCounter: 0
        };
    }

    render() {
        return (
            <div className="App" style={{height: window.innerHeight}}>
                <Search handleClick={this.handleClick} handleChange={this.handleChange}/>
                <Webpage
                    url={this.state.url}
                    primaryCounter={this.state.primaryCounter}
                    secondaryCounter={this.state.secondaryCounter}
                />
            </div>
        );
    }

    // "http://192.168.1.36:8080/http://clips.vorwaerts-gmbh.de/VfE_html5.mp4"

    handleClick = () => {
        if (this.state.clickCount === 0) {
            this.setState({
                url: `http://192.168.1.36:8080/${this.state.address}***`,
                clickCount: 1
            });
            setInterval(() => {
                this.setState({
                    primaryCounter: ++this.state.primaryCounter
                })
            }, 1000);
        } else if (this.state.clickCount === 1) {
            this.setState({
                url: `http://192.168.1.36:8080/${this.state.address}****`,
                clickCount: 0
            });
            setInterval(() => {
                this.setState({
                    secondaryCounter: ++this.state.secondaryCounter
                })
            }, 1000);
        }
    };

    handleChange = (event) => {
        this.setState({[event.target.name]: event.target.value})
    };
}