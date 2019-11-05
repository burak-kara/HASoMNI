import React, {Component} from 'react';

export default class SearchButton extends Component {
    render() {
        return (
            <button
                className="searchButton"
                onClick={this.props.handleClick}
            >
                Search
            </button>
        );
    }
}