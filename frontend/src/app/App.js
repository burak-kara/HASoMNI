import React, {Component} from 'react';
import './App.css';
import Search from "../components/search/Search";
import Webpage from "../components/webpage/Webpage";

export default class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            address: "",
            content: ""
        };
    }

    render() {
        return (
            <div className="App" style={{height: window.innerHeight}}>
                <Search handleClick={this.handleClick} handleChange={this.handleChange}/>
                <Webpage content={this.state.content}/>
            </div>
        );
    }

    handleChange = (event) => {
        this.setState({[event.target.name]: event.target.value})
    };

    // "http://192.168.1.35:8080/http://clips.vorwaerts-gmbh.de/VfE_html5.mp4"

    handleClick = () => {
        console.log(this.state.address);
        const url = `http://192.168.1.35:8080/${this.state.address}***`;
        console.log(url);
        this.setState({
            content: url
        });
    };
}