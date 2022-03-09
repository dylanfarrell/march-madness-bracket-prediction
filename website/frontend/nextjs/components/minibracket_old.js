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
import win_probs from './win_probs';

const scoring = {
    '1':320/64,
    '2':320/32,
    '3':320/16,
    '4':320/8,
    '5':320/4,
    '6':320/2,
    '7':320/1
}

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

export default function MiniBracket(props) {
  // round 4
  const blank = "_________";
  const [r4g1, setr4g1] = useState({
    team1: blank,
    team2: blank,
    value: null,
    child: null,
    round: '4',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  // round 3
  const [r3g1, setr3g1] = useState({
    team1: blank,
    team2: blank,
    value: null,
    child: { g: r4g1, f: setr4g1, pos: 1 },
    round: '3',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r3g2, setr3g2] = useState({
    team1: blank,
    team2: blank,
    value: null,
    child: { g: r4g1, f: setr4g1, pos: 2 },
    round: '3',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  // round 2
  const [r2g1, setr2g1] = useState({
    team1: blank,
    team2: blank,
    value: null,
    child: { g: r3g1, f: setr3g1, pos: 1 },
    round: '2',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r2g2, setr2g2] = useState({
    team1: blank,
    team2: blank,
    value: null,
    child: { g: r3g1, f: setr3g1, pos: 2 },
    round: '2',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r2g3, setr2g3] = useState({
    team1: blank,
    team2: blank,
    value: null,
    child: { g: r3g2, f: setr3g2, pos: 1 },
    round: '2',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r2g4, setr2g4] = useState({
    team1: blank,
    team2: blank,
    value: null,
    child: { g: r3g2, f: setr3g2, pos: 2 },
    round: '2',
    team1WinProb: 0.5,
    expectedPoints:0
  });

  // round 1
  const [r1g1, setr1g1] = useState({
    team1: matchups[0][0],
    team2: matchups[0][1],
    value: null,
    child: { g: r2g1, f: setr2g1, pos: 1 },
    round: '1',
    team1WinProb: 0.8,
    expectedPoints:0
  });
  const [r1g2, setr1g2] = useState({
    team1: matchups[1][0],
    team2: matchups[1][1],
    value: null,
    child: { g: r2g1, f: setr2g1, pos: 2 },
    round: '1',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r1g3, setr1g3] = useState({
    team1: matchups[2][0],
    team2: matchups[2][1],
    value: null,
    child: { g: r2g2, f: setr2g2, pos: 1 },
    round: '1',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r1g4, setr1g4] = useState({
    team1: matchups[3][0],
    team2: matchups[3][1],
    value: null,
    child: { g: r2g2, f: setr2g2, pos: 2 },
    round: '1',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r1g5, setr1g5] = useState({
    team1: matchups[4][0],
    team2: matchups[4][1],
    value: null,
    child: { g: r2g3, f: setr2g3, pos: 1 },
    round: '1',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r1g6, setr1g6] = useState({
    team1: matchups[5][0],
    team2: matchups[5][1],
    value: null,
    child: { g: r2g3, f: setr2g3, pos: 2 },
    round: '1',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r1g7, setr1g7] = useState({
    team1: matchups[6][0],
    team2: matchups[6][1],
    value: null,
    child: { g: r2g4, f: setr2g4, pos: 1 },
    round: '1',
    team1WinProb: 0.5,
    expectedPoints:0
  });
  const [r1g8, setr1g8] = useState({
    team1: matchups[7][0],
    team2: matchups[7][1],
    value: null,
    child: { g: r2g4, f: setr2g4, pos: 2 },
    round: '1',
    team1WinProb: 0.5,
    expectedPoints:0
  });

  const games = [r1g1,r1g2,r1g3,r1g4,r1g5,r1g6,r1g7,r1g8,r2g1,r2g2,r2g3,r2g4,r3g1,r3g2,r4g1];

  const getTotalExpectedPoints = (games) => {
    let total = 0
    games.forEach((x,i) => total += x.expectedPoints)
    return total
};

  const handleChange = (val, setValue, set) => (event) => {
    if (set) {
        let pts = 10
        if (event.target.value == val.team1) {
            pts = val.team1WinProb*scoring[val.round]
        } else {
            pts = (1-val.team1WinProb)*scoring[val.round]
        }
      props.setExpectedPoints(getTotalExpectedPoints(games)+pts-val.expectedPoints);
      setValue((state) => ({ ...state, value: event.target.value, expectedPoints:pts}));
    }
    if (val.child) {
      if (val.child.pos == 1) {
        val.child.f((state) => ({ ...state, team1: event.target.value }));
      } else {
        val.child.f((state) => ({ ...state, team2: event.target.value }));
      }
      console.log(val.child.g.team1)
      const combo = val.child.g.team1.concat(", ",val.child.g.team2)
      if (combo in win_probs) {
          val.child.f((state) => ({...state, team1WinProb:win_probs[combo]}));
      } else {
        val.child.f((state) => ({...state, team1WinProb:0.5}));
      }
      if (
        val.child.g.value != val.child.g.team1 &&
        val.child.g.value != val.child.g.team2
      ) {
        val.child.f((state) => ({ ...state, value: null, expectedPoints:0}));
        handleChange(val.child.g, val.child.f, 0)({ target: { value: blank } });
      } else if (val.child.g.value == val.child.g.team1) {
          val.child.f((state) => ({...state, expectedPoints:val.child.g.team1WinProb*scoring[val.child.g.round]}));
      } else {
        val.child.f((state) => ({...state, expectedPoints:(1-val.child.g.team1WinProb)*scoring[val.child.g.round]}));
      }
    }
  };

  return (
    <Stack direction="row" spacing={4}>
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={2}
        sx={{ height: 1200 }}
      >
        <Game
          {...r1g1}
          handleChange={(event) => handleChange(r1g1, setr1g1, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g1, setr1g1)(pts)}
        />
        <Game
          {...r1g2}
          handleChange={(event) => handleChange(r1g2, setr1g2, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g2, setr1g2)(pts)}

        />
        <Game
          {...r1g3}
          handleChange={(event) => handleChange(r1g3, setr1g3, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g3, setr1g3)(pts)}

        />
        <Game
          {...r1g4}
          handleChange={(event) => handleChange(r1g4, setr1g4, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g4, setr1g4)(pts)}

        />
        <Game
          {...r1g5}
          handleChange={(event) => handleChange(r1g5, setr1g5, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g5, setr1g5)(pts)}

        />
        <Game
          {...r1g6}
          handleChange={(event) => handleChange(r1g6, setr1g6, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g6, setr1g6)(pts)}

        />
        <Game
          {...r1g7}
          handleChange={(event) => handleChange(r1g7, setr1g7, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g7, setr1g7)(pts)}

        />
        <Game
          {...r1g8}
          handleChange={(event) => handleChange(r1g8, setr1g8, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r1g8, setr1g8)(pts)}

        />
      </Stack>
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={16}
        sx={{ height: 1200 }}
      >
        <Game
          {...r2g1}
          handleChange={(event) => handleChange(r2g1, setr2g1, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r2g1, setr2g1)(pts)}

        />
        <Game
          {...r2g2}
          handleChange={(event) => handleChange(r2g2, setr2g2, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r2g2, setr2g2)(pts)}

        />
        <Game
          {...r2g3}
          handleChange={(event) => handleChange(r2g3, setr2g3, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r2g3, setr2g3)(pts)}

        />
        <Game
          {...r2g4}
          handleChange={(event) => handleChange(r2g4, setr2g4, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r2g4, setr2g4)(pts)}

        />
      </Stack>
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={47}
        sx={{ height: 1200 }}
      >
        <Game
          {...r3g1}
          handleChange={(event) => handleChange(r3g1, setr3g1, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r3g1, setr3g1)(pts)}

        />
        <Game
          {...r3g2}
          handleChange={(event) => handleChange(r3g2, setr3g2, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r3g2, setr3g2)(pts)}

        />
      </Stack>
      <Stack alignItems="center" justifyContent="center" sx={{ height: 1200 }}>
        <Game
          {...r4g1}
          handleChange={(event) => handleChange(r4g1, setr4g1, 1)(event)}
          setExpectedPoints={(pts) => setExpectedPoints(r4g1, setr4g1)(pts)}

        />
      </Stack>
    </Stack>
  );
}
