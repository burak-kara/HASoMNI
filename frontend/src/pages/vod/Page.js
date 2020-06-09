import React, {Component} from 'react';
import ReactSpeedometer from "react-d3-speedometer";
import {Replay} from "vimond-replay";
import "./Page.css";

export default class VodPage extends Component {
    render() {
        return (
            <div className="container-fluid page-container">
                <div className="row content-row">
                    {this.renderContent()}
                </div>
                {/*<div className="row stats-row">*/}
                {/*    {this.singleConnectionStats()}*/}
                {/*    {this.hybridConnectionStats()}*/}
                {/*</div>*/}
            </div>
        );
    };

    renderContent = () => {
        if (this.props.url && this.props.url !== "") {
            return (
                <div className="col content-col">
                    <Replay
                        source={this.props.url}
                        initialPlaybackProps={{ isPaused: true }}
                    />
                </div>
            );
        } else {
            return (
                <div className="col placeholder">
                    Video content will be here
                </div>
            );
        }
    };

    singleConnectionStats = () => {
        return (
            <div className="col stats-column">
                <label className="stats-title">
                    Single Interface
                </label>
                <ReactSpeedometer
                    needleColor="black"
                    startColor="green"
                    endColor="red"
                    needleTransition="easeElastic"
                    value={this.props.singleCounter}
                    currentValueText={`${this.props.singleCounter} secs`}
                    maxValue={60}
                    segments={1000}
                    maxSegmentLabels={8}
                    needleTransitionDuration={1000}
                    needleHeightRatio={0.7}
                    ringWidth={40}
                    paddingVertical={20}
                />
                <label>
                    {this.props.singleBytes} Bytes
                </label>
                <label>
                    {this.convertToMB(this.props.singleBytes)} MB
                </label>
            </div>
        );
    };

    convertToMB = (bytes) => {
        return (bytes / (1024 * 1024)).toFixed(2);
    };

    hybridConnectionStats = () => {
        return (
            <div className="col stats-column">
                <label className="stats-title">
                    Multiple Interfaces
                </label>
                <ReactSpeedometer
                    needleColor="black"
                    startColor="green"
                    endColor="red"
                    needleTransition="easeElastic"
                    value={this.props.hybridCounter}
                    currentValueText={`${this.props.hybridCounter} secs`}
                    maxValue={60}
                    segments={1000}
                    maxSegmentLabels={8}
                    needleTransitionDuration={1000}
                    needleHeightRatio={0.7}
                    ringWidth={40}
                    paddingVertical={20}
                />
                <label>
                    {this.props.hybridBytes} Bytes
                </label>
                <label>
                    {this.convertToMB(this.props.hybridBytes)} MB
                </label>
            </div>
        );
    };
}