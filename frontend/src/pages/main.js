import React from "react";
import { useHistory } from 'react-router-dom';

const Main = () => {
    const history = useHistory();
    return (
        <div className="container-fluid">
            <div className="row main-navigator-row">
                <div className="col-6 main-navigator-col">
                    <button className="btn btn-primary" onClick={() => history.push("/vod")}>VoD</button>
                </div>
                <div className="col-6 main-navigator-col">
                    <button className="btn btn-danger" onClick={() => history.push("/live")}>Live</button>
                </div>
            </div>
        </div>
    );
}

export default Main;