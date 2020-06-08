import React, {Component} from 'react';
import Search from "../../components/search/Search";
import LivePage from "./Page";
import {GATEWAY_IP} from "../../_utils/Utils";

export default class Live extends Component {
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
            <>
                <Search handleClick={this.handleClick} handleChange={this.handleChange}/>
                <LivePage
                    url={this.state.url}
                    singleCounter={this.state.singleCounter}
                    singleBytes={this.state.singleBytes}
                    hybridCounter={this.state.hybridCounter}
                    hybridBytes={this.state.hybridBytes}
                />
            </>
        );
    }

    handleChange = (event) => {
        this.setState({[event.target.name]: event.target.value})
    };

    handleClick = () => {
        this.setState({url: `${GATEWAY_IP}${this.state.address}`})
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