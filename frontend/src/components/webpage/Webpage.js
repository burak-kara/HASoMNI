import React, {Component} from 'react';
import ReactSpeedometer from "react-d3-speedometer";
import "./Webpage.css";

export default class Webpage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            secs: 0
        }
    }

    componentDidMount() {
        this.testCounter();
    }

    render() {
        return (
            <div className="container-fluid webPageContainer">
                <div className="row contentRow">
                    {this.renderContent()}
                </div>
                <div className="row statsRow">
                    <div className="col primaryConnection">
                        <label className="primaryConnectionLabel">
                            Single Connection
                        </label>
                        <ReactSpeedometer
                            needleColor="black"
                            startColor="green"
                            endColor="red"
                            needleTransition="easeElastic"
                            value={this.props.primaryCounter}
                            maxValue={90}
                            segments={1000}
                            maxSegmentLabels={9}
                            needleTransitionDuration={1000}
                            needleHeightRatio={0.7}
                            ringWidth={40}
                            paddingVertical={20}
                        />
                        <label>
                            Time: {this.props.primaryCounter}
                        </label>
                        <label>
                            Bytes: {this.state.secs}
                        </label>
                    </div>
                    <div className="col secondaryConnection">

                    </div>
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

    testCounter = () => {
        setInterval(() => {
            this.setState({
                secs: ++this.state.secs
            })
        }, 1000);
    };
}