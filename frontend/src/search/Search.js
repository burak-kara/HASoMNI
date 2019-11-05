import React, {Component} from 'react';
import "./Search.css";
import SearchBar from "./SearchBar";
import SearchButton from "./SearchButton";
import {FaInfoCircle} from 'react-icons/fa';
import Tooltip from 'react-tooltip-lite';

export default class Search extends Component {
    render() {
        return (
            <div className="searchContainer">
                <Tooltip
                    content={(
                        <div>
                            Test files are test20mb and test150mb <br/>
                            Also, you can use it as search engine. <br/>
                            We will serve over www.google.com
                        </div>
                    )}
                    className="target"
                    eventOn="onMouseOver"
                    eventOff="onMouseOut"
                    tagName="span"
                    direction="down-start"
                    tipContentHover={true}
                    arrowSize={5}
                    styles={{alignSelf: 'center'}}
                >
                    <FaInfoCircle
                        style={{color: "#3c2f2f", alignSelf: 'center', fontSize: '150%'}}
                    />
                </Tooltip>
                <SearchBar handleChange={this.props.handleChange}/>
                <SearchButton handleClick={this.props.handleClick}/>
            </div>
        );
    };
}