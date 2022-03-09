import * as React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import ProTip from "../src/ProTip";
import Link from "../src/Link";
import Copyright from "../src/Copyright";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Game from "./game";
import { styled } from "@mui/material/styles";
import Paper from "@mui/material/Paper";
import { useRef, useEffect, useState } from "react";
import win_probs from "./win_probs";

const scoring = {
  1: 320 / 64,
  2: 320 / 32,
  3: 320 / 16,
  4: 320 / 8,
  5: 320 / 4,
  6: 320 / 2,
  7: 320 / 1,
};

const matchups = [
  ["1 Gonzaga", "16 Norfolk St"],
  ["8 Oklahoma", "9 Missouri"],
  ["5 Creighton", "12 UCSB"],
  ["4 Virgina", "13 Ohio"],
  ["6 USC", "11 Drake"],
  ["3 Kansas", "14 E Washington"],
  ["7 Oregon", "10 VCU"],
  ["2 Iowa", "15 GCU"],
];

const blank = "_________";

const default_game = {
  team1: blank,
  team2: blank,
  team1_w_prob: 0.5,
  team2_w_prob: 0.5,
  value: null,
  expected_points: null,
};

export default function MiniBracket(props) {
  let games = Array(Math.pow(matchups.length,2)-1);
  for (let i = 0; i < 8; i++) {
    games[i] = useState({
      team1: matchups[i][0],
      team2: matchups[i][1],
      team1_w_prob: win_probs[matchups[i][0].concat(", ", matchups[i][1])],
      team2_w_prob: 1 - win_probs[matchups[i][0].concat(", ", matchups[i][1])],
      value: null,
      expected_points: null,
      round:1
    });
  }

  console.log(games[0][0])

  for (let i = 8; i < 12; i++) {
    games[i] = useState({...default_game, round:2});
  }

  for (let i = 12; i < 14; i++) {
    games[i] = useState({...default_game, round:3});
  }

  for (let i = 14; i < 15; i++) {
    games[i] = useState({...default_game, round:4});
  }

  const [pts, setPoints] = useState(0);

  const updatePts = () => {
    const total = 0;
    games.forEach((game) => (total += game.expected_points));
    setPoints(total);
  };

  const getWProb = (t1, t2) => {
    combo = t1.concat(", ", t2);
    if (combo in win_probs) {
      return win_probs[combo];
    } else {
      return 0.5;
    }
  };
  const hasChild = (game) => {
    return game < games.length - 1;
  };
  const getChildIdx = (game) => {
    return (game % 2) + 1;
  };
  const getChild = (game) => {
    return (
      Math.floor((game - games_before_round[games[game][0].round]) / 2) +
      games_through_round[games[game][0].round]
    );
  };

  const updateTeams = (game, idx, new_val) => {
    if (idx == 1) {
      if (games[game][0].value == games[game][0].team1) {
        games[game][1](
          (state) => ({
            ...state,
            team1: new_val,
            value: null,
            expected_points: 0,
          }),
          function () {
            if (hasChild(game)) {
              updateTeams(getChild(game), getChildIdx(game), blank);
            }
          }
        );
      } else {
        games[game][1]((state) => ({
          ...state,
          team1_w_prob: getWProb(new_val, state.team2),
          team1: new_val,
          expected_points: new_val * getWProb(new_val, state.team2),
        }));
      }
    } else {
      if (games[game][0].value == games[game][0].team2) {
        games[game][1](
          (state) => ({
            ...state,
            team2: new_val,
            value: null,
            expected_points: 0,
          }),
          function () {
            if (hasChild(game)) {
              updateTeams(getChild(game), getChildIdx(game), blank);
            }
          }
        );
      } else {
        games[game][1]((state) => ({
          ...state,
          team1_w_prob: getWProb(state.team1, new_val),
          team2: new_val,
          expected_points: new_val * getWProb(state.team1, new_val),
        }));
      }
    }
  };

  const handleChange = (game) => (event) => {
    games[game][1](
      (state) => ({
        ...state,
        value: event.target.value,
        expected_points: state.team1_w_prob * scoring[state.round],
      })
    );
    console.log(games[game][0].expected_points)
  };

  const renderGame = (i) => {
    return (
      <Game key={i} {...games[i][0]} handleChange={(event) => handleChange(i)(event)} />
    );
  };

  return (
    <Stack direction="row" spacing={4}>
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={2}
        sx={{ height: 1200 }}
      >
        <Game {...games[0][0]} handleChange={(event) => handleChange(0)(event)}/>
        {Array(8)
          .fill(0)
          .map((x, i) => {
            return renderGame(i);
          })}
      </Stack>
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={16}
        sx={{ height: 1200 }}
      >
        {Array(4)
          .fill(0)
          .map((x, i) => {
            return renderGame(i + 8);
          })}
      </Stack>
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={47}
        sx={{ height: 1200 }}
      >
        {Array(2)
          .fill(0)
          .map((x, i) => {
            return renderGame(i + 8);
          })}
      </Stack>
      <Stack alignItems="center" justifyContent="center" sx={{ height: 1200 }}>
        {Array(2)
          .fill(0)
          .map((x, i) => {
            return renderGame(i + 8);
          })}
      </Stack>
    </Stack>
  );
}
