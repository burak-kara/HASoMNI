import React, {Component} from 'react';
import Search from "../../components/search/Search";
import VodPage from "./Page";
import {GATEWAY_IP} from "../../_utils/Utils";

export default class Vod extends Component {
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
                <VodPage
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
}