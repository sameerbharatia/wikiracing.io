import React from 'react';
import "./Users.css";

function Users({ roomData }) {

    // TODO: fix how we're doing emojis

     const usersHTML = roomData['data'] ? Object.values(roomData['data']['users']).sort((a, b) => b['wins']-a['wins']).map((user) => {
        return (
        <div className='player'>
        <div className="emoji"><p><span role="img">{user['emoji']}</span></p></div>
        <div className="text">
        <p className="username">{user['username']}</p>
        <p className="wins">{user['wins']}<span className="tool-tip">wins</span></p>
        </div>
        <div className='info-container'>
        <p className="admin">{user['admin'] ? '&#128737;&#65039;' : null }</p>
        </div>
        </div>
        )
        }) : null

    return (
        <div className='users-container'>

        <h2>LEADERBOARD</h2>
        <div className='players-container'>
            {usersHTML}
        </div>

        </div>

    )

}

export default Users;
