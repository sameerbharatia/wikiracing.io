import React, { useState, useEffect } from "react";
import { socket } from "./Socket";
import { useParams, Navigate, Link, useNavigate } from "react-router-dom";
import parse from 'html-react-parser';
import Watch from "./Watch";
import "./WikiPage.css";


function WikiPage({ roomCode }) {
  const [pageData, setPageData] = useState({});
  const [userData, setUserData] = useState({});
  const [time, setTime] = useState(0);
  const [winner, setWinner] = useState({});
  const [gameOver, setGameOver] = useState(false);
  let { wikiPage } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
     async function fetchPageData() {
      try {
        const response = await fetch(`https://en.wikipedia.org/api/rest_v1/page/html/${wikiPage}`);
        const data = await response.text();
        setPageData({
          title: wikiPage.replaceAll("_", " "),
          html: data
        });
        window.scrollTo(0, 0);
      } catch (error) {
        console.error(error);
      }
    }

    fetchPageData();

    socket.on("updatePage", (data) => {
      console.log(data);
      setUserData(data);
    });

    socket.emit("updatePage", { roomCode, wikiPage });


    socket.on("endRound", (winnerData) => {
      console.log("Receving endRound call, emitting time");
      setGameOver(true);
      setWinner(winnerData);
      socket.emit("updateTime", { roomCode, time: time + 1 });
      /* setTimeout(() => {
        navigate(`/game/${roomCode}`);
      }, 5000);  */
    });

    // Don't let users use the back-button
    // Navigate forward if back button is pressed
    window.addEventListener("popstate", () => {
      navigate(1);
    });

    return () => {
      socket.off("updatePage");
      socket.off("endRound");
    }

  }, [wikiPage]);

  function formatTime(seconds) {
    const minutes = Math.floor(seconds/60)
    const rem_seconds = seconds % 60;

    function str_pad_left(string,pad,length) {
        return (new Array(length+1).join(pad)+string).slice(-length);
    }

    return str_pad_left(minutes,'0',2)+':'+str_pad_left(rem_seconds,'0',2)
  }


  return roomCode === "" ? (
    <Navigate to="/" />
  ) : (
    <div className="wiki-container">
      {gameOver ? (
        <div className="winner-overlay">
          <h1 className="winner-name">&#127942;{winner["username"]} won!</h1>
          <p className="winner-time"><b>&#128336; Time</b>	{formatTime(time)}</p>
          <p className="winner-clicks"><b>&#128433;&#65039; Clicks</b> {winner["clicks"]}</p>
          <Link to={`/game/${roomCode}`}><button className="overlay-btn">CONTINUE</button></Link>
        </div>
      ) : null}

      <div className="stats-container">
        <Watch time={time} setTime={setTime} gameOver={gameOver} />
        <div className="target-container">Target: {userData["target"]}</div>
      </div>

      <div className="mediawiki ltr sitedir-ltr mw-hide-empty-elt ns-0 ns-subject mw-editables skin-vector action-view skin-vector-legacy minerva--history-page-action-enabled">
        <div id="content" className="mw-body-content background" role="main">
          <div id="content" className="mw-body" role="main">
            <h1 id="firstHeading" className="firstHeading" lang="en">
              {pageData["title"]}
            </h1>

            <div id="bodyContent" className="mw-body-content"></div>
            <div id="siteSub" className="noprint">
              From Wikipedia, the free encyclopedia
            </div>
            <div id="contentSub"></div>
            <div
              id="mw-content-text"
              lang="en"
              dir="ltr"
              className="mw-content-ltr"
            >
              <div>
                {/* Add more rules for parsing HTML (remove links to other websites etc.) */}
                {parse(String(pageData["html"]),
                {
                  replace: node => {
                    if (
                      node.type === "tag" &&
                      node.name === "a" &&
                      node.children[0] &&
                      node.attribs.title
                    ) {
                      return <Link to={`/wiki/${node.attribs.href.slice(2)}`}>{node.children[0].data}</Link>;
                     } else if (
                      node.type === "tag" &&
                      node.name === "base"
                    ) {
                      node.attribs.href = "";
                    } else if (
                      node.type === "tag" &&
                      node.name === "link" &&
                      node.attribs.rel === "stylesheet"
                    ) {
                      node.attribs.href = `//en.wikipedia.org/${node.attribs.href}`;
                    } else if (
                      node.type === "tag" &&
                      node.name === "a" &&
                      node.attribs.class === "external text"
                    ) {
                      return <span>{node.children[0].data}</span>;
                    }
                   }
                  }
                 )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WikiPage;
