import React, {Component} from 'react';
import {FaInfoCircle} from 'react-icons/fa';
import Tooltip from 'react-tooltip-lite';

export default class Tip extends Component {
    render() {
        return(
            <Tooltip
                content={(
                    <div>
                        Enter full path http or https <br/>
                        e.g. http://site/path <br/>
                        for test server use this as a source root <br/>
                        http://3.134.95.115:8080/ <br/>
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
        );
    }
}