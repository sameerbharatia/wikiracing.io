import React from "react";
import { useForm } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import { useNavigate } from "react-router-dom";
import { backend_url } from "./Socket";
import "./LoginPage.css";

function JoinGame({ setUserName, setRoomCode }) {
  const navigate = useNavigate();
  const { register, handleSubmit, errors } = useForm();
  const ROOM_LIMIT = 8;

  async function onSubmit(data) {
    setUserName(data.userName);
    const roomCode = data.roomCode;
    setRoomCode(String(roomCode));
    navigate(`/game/${roomCode}`);
  }

  return (
    <div className="wrapper">
      <div className="wrapper centered">
        <div className="title-container">
          <h1 className="title">wikiracing.io</h1>
        </div>

        <form autoComplete="off" onSubmit={handleSubmit(onSubmit)}>
          <div className="form-container">
            <input
              className="main-input"
              autoFocus
              placeholder="Username"
              name="userName"
              ref={register({
                required: "Username is required.",
                minLength: {
                  value: 3,
                  message: "You need at least 3 characters.",
                },
                maxLength: {
                  value: 20,
                  message: "You need less than 20 characters.",
                },
              })}
            />
            <ErrorMessage errors={errors} name="userName" as="p" />

            <input
              className="main-input"
              placeholder="Room Code"
              name="roomCode"
              ref={register({
                required: "Room Code is required.",
                pattern: {
                  value: /^\d{4}$/,
                  message: "Room Code must be a 4 digit number.",
                },
                validate: async (roomCode) => {
                  let valid = fetch(backend_url + "/validation_data")
                    .then((res) => {
                      return res.json();
                    })
                    .then((data) => {
                      let error = true;
                      if (!Object.keys(data).includes(roomCode))
                        error = "This room does not exist.";
                      else if (
                        Object.keys(data[roomCode]["users"]).length >=
                        ROOM_LIMIT
                      )
                        error = "This room is full.";
                        console.log(error)
                      return error;
                    });

                  return valid;
                },
              })}
            />
            <ErrorMessage errors={errors} name="roomCode" as="p" />
          </div>

          <div className="button-container">
            <button className="home-btn main-button" type="submit">
              JOIN GAME
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default JoinGame;
