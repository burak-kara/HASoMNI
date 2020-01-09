import React, {Component} from 'react';
import Tip from "./Tip";
import SearchBar from "./SearchBar";
import SearchButton from "./SearchButton";
import "./Search.css";

export default class Search extends Component {
    render() {
        return (
            <div className="searchContainer">
                <Tip/>
                <SearchBar handleChange={this.props.handleChange}/>
                <SearchButton handleClick={this.props.handleClick}/>
            </div>
        );
    };
}