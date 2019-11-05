import React, {Component} from 'react';

export default class SearchBar extends Component {
    render() {
        return (
            <input
                className="searchBar"
                type="text"
                name="address"
                placeholder="Search..."
                onChange={this.props.handleChange}
            />
        );
    }
}