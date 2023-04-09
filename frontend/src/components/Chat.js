import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { socket } from "./Socket"
import './Chat.css'
import SendIcon from '@mui/icons-material/Send';

function Chat({userName, roomCode}) {

    // TODO: fix how we're doing emojis

    const [chatMSGS, setchatMSGS] = useState([]);
    const { register, handleSubmit } = useForm();


    useEffect(() => {
        socket.on("chatMSG", (msg) => {
            setchatMSGS((prev) => [...prev, msg]);
          });

        return () => {
            socket.off("chatMSG");
        }
    }, [])


    function onChat(data, e) {
        socket.emit('chatMSG', {userName, roomCode, 'message': data.chatMSG})
        console.log(chatMSGS)
        e.target.reset()
      }

      const msgItems = chatMSGS.map((msg) => (
      <div className='message'><p key={msg['message']}><span role="img">{msg['emoji']}</span> <b>{msg['username']}:</b> {msg['message']}</p></div>
          ));


  return(
      <div className='chat-container'>
      <h2>CHAT</h2>
      <div className="messages-container">
          {msgItems}
      </div>
      <div className="chat-form-container">
      <form onSubmit={handleSubmit(onChat)}>
        <input
            autoComplete='off'
            placeholder="Send message"
            {...register("chatMSG", { required: true })}
            />
        <button type="submit"><SendIcon /></button>
      </form>
      </div>
      </div>
  )
}

export default Chat;
