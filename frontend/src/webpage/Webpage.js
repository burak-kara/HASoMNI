import React, {Component} from 'react';
import "./Webpage.css";

export default class Webpage extends Component {
    render() {
        return (
            // TODO change css of this components
            // shows two scrollbar
            <div className="webpageContainer">
                <td className="webpageContainer" dangerouslySetInnerHTML={{__html: this.props.content}} />
            </div>
        );
    };
}