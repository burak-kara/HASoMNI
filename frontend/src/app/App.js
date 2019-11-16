import React, {Component} from 'react';
import './App.css';
import Search from "../search/Search";
import Webpage from "../webpage/Webpage";

class App extends Component {
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

    // handleClick = () => {
    //     fetch(`http://54.91.200.127:8080/34.204.97.0:8080/${this.state.address}`, {
    //         method: 'GET'
    //     }).then(response => {
    //     });
    // };

    // gets full path with server address and port
    // TODO whatever given, process it if it is test files serve them
    // if not serve over google.com like search engine
    handleClick = () => {
        let xhr = new XMLHttpRequest();
        xhr.addEventListener('load', () => {
            // update the state of the component with the result here
            this.setState({content: xhr.response}, ()=> {});
            console.log(xhr.responseText); // TODO delete
        });
        console.log(this.state.address); // TODO delete
        xhr.open('GET', `http://${this.state.address}`);
        xhr.send();
    };
}

export default App;
