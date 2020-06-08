import React, {Component} from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Live from "../pages/live";
import Vod from "../pages/vod";
import Main from "../pages/main";
import './App.css';

export default class App extends Component {
    render() {
        return (
            <Router>
                <div className="App" style={{height: window.innerHeight}}>
                    <Switch>
                        <Route path={"/vod"} component={Vod}/>
                        <Route exact path={"/live"} component={Live}/>
                        <Route path={"*"} component={Main}/>
                    </Switch>
                </div>
            </Router>
        );
    }
}