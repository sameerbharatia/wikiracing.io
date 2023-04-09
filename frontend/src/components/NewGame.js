import React from "react";
import { useForm } from "react-hook-form";
import { ErrorMessage } from "@hookform/error-message";
import { useNavigate } from "react-router-dom";
import { backend_url } from "./Socket";
import "./LoginPage.css";

function NewGame({ setUserName, setRoomCode }) {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = (data) => {
    setUserName(data.userName);

    //generate a new, unique room code and go to new room
    // const requestOptions = {
    //   headers: {
    //     'Access-Control-Allow-Origin' : '*',
    //     'Access-Control-Allow-Methods':'GET,PUT,POST,DELETE,PATCH,OPTIONS',
    //     }
    // };
    fetch(backend_url + "/validation_data")
      .then((res) => {
        return res.json();
      })
      .then((data) => {
        let room = Math.floor(1000 + Math.random() * 9000);
        while (room in Object.keys(data)) {
          room = Math.floor(1000 + Math.random() * 9000);
        }
        setRoomCode(String(room))
        navigate(`/game/${room}`);
      });

  };

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
              {...register("userName", {
                required: "Username is required.",
                minLength: {
                  value: 3,
                  message: "You need at least 3 characters.",
                },
                maxLength: {
                  value: 20,
                  message: "You need less than 15 characters.",
                },
              })}
            />
            <ErrorMessage errors={errors} name="userName" as="p" />
          </div>
          <div className="button-container">
            <button className="home-btn main-button" type="submit">
              START GAME
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}

export default NewGame;
