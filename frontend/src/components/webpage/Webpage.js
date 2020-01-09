import React, {Component} from 'react';
import ReactSpeedometer from "react-d3-speedometer";
import "./Webpage.css";

export default class Webpage extends Component {
    render() {
        return (
            <div className="container-fluid page-container">
                <div className="row content-row">
                    {this.renderContent()}
                </div>
                <div className="row stats-row">
                    {this.singleConnectionStats()}
                    {this.hybridConnectionStats()}
                </div>
            </div>
        );
    };

    renderContent = () => {
        if (this.props.url && this.props.url !== "") {
            return (
                <video key={this.props.url} autoPlay={true} controls={true}>
                    <source src={this.props.url}/>
                </video>
            );
        } else {
            return (
                <div className="placeholder">
                    Video content will be here
                </div>
            );
        }
    };

    singleConnectionStats = () => {
        return (
            <div className="col stats-column">
                <label className="stats-title">
                    Single Connection
                </label>
                <ReactSpeedometer
                    needleColor="black"
                    startColor="green"
                    endColor="red"
                    needleTransition="easeElastic"
                    value={this.props.singleCounter}
                    maxValue={60}
                    segments={1000}
                    maxSegmentLabels={8}
                    needleTransitionDuration={1000}
                    needleHeightRatio={0.7}
                    ringWidth={40}
                    paddingVertical={20}
                />
                <label>
                    Bytes: {this.props.singleBytes}
                </label>
            </div>
        );
    };

    hybridConnectionStats = () => {
        return (
            <div className="col stats-column">
                <label className="stats-title">
                    Hybrid Connection
                </label>
                <ReactSpeedometer
                    needleColor="black"
                    startColor="green"
                    endColor="red"
                    needleTransition="easeElastic"
                    value={this.props.hybridCounter}
                    maxValue={60}
                    segments={1000}
                    maxSegmentLabels={8}
                    needleTransitionDuration={1000}
                    needleHeightRatio={0.7}
                    ringWidth={40}
                    paddingVertical={20}
                />
                <label>
                    Bytes: {this.props.hybridBytes}
                </label>
            </div>
        );
    };
}