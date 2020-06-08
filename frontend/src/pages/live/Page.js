import React from 'react';
import ReactSpeedometer from "react-d3-speedometer";
import {Replay} from "vimond-replay";
import ShakaVideoStreamer from 'vimond-replay/video-streamer/shaka-player';
import "./Page.css";

const LivePage = props => {

    const renderContent = () => {
        if (props.url && props.url !== "") {
            return (
                <div className="col content-col">
                    <Replay
                        source="https://storage.googleapis.com/shaka-demo-assets/angel-one/dash.mpd"
                        initialPlaybackProps={{isPaused: true}}
                    >
                        <ShakaVideoStreamer/>
                    </Replay>
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

    const singleConnectionStats = () => {
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
                    value={props.singleCounter}
                    currentValueText={`${props.singleCounter} secs`}
                    maxValue={60}
                    segments={1000}
                    maxSegmentLabels={8}
                    needleTransitionDuration={1000}
                    needleHeightRatio={0.7}
                    ringWidth={40}
                    paddingVertical={20}
                />
                <label>
                    {props.singleBytes} Bytes
                </label>
                <label>
                    {convertToMB(props.singleBytes)} MB
                </label>
            </div>
        );
    };

    const convertToMB = (bytes) => (bytes / (1024 * 1024)).toFixed(2);

    const hybridConnectionStats = () => {
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
                    value={props.hybridCounter}
                    currentValueText={`${props.hybridCounter} secs`}
                    maxValue={60}
                    segments={1000}
                    maxSegmentLabels={8}
                    needleTransitionDuration={1000}
                    needleHeightRatio={0.7}
                    ringWidth={40}
                    paddingVertical={20}
                />
                <label>
                    {props.hybridBytes} Bytes
                </label>
                <label>
                    {convertToMB(props.hybridBytes)} MB
                </label>
            </div>
        );
    };

    return (
        <div className="container-fluid page-container">

            <div className="row content-row">
                {renderContent()}
            </div>
            <div className="row stats-row">
                {singleConnectionStats()}
                {hybridConnectionStats()}
            </div>
        </div>
    );
}

export default LivePage;