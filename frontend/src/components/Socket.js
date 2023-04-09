import io from "socket.io-client";

// TODO: make socket not connect on launch; connect it in Game.js instead (?)

export const backend_url = "http://127.0.0.1:5001/"
export const socket = io(backend_url);
