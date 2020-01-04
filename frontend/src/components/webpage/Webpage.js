import React, {Component} from 'react';
import {Player} from 'video-react';
import "./Webpage.css";

export default class Webpage extends Component {
    render() {
        if (this.props.content && this.props.content !== "") {
            return (
                <video key={this.props.content} autoPlay={true} controls={true}>
                    <source src={this.props.content}/>
                </video>
            );
        } else {
            return (
                <td className="webpageContainer" dangerouslySetInnerHTML={{__html: this.props.content}}/>
            );
        }
    };
}