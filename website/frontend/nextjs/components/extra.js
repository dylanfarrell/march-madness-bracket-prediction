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
import Game from "../components/game";
import { styled } from "@mui/material/styles";
import Paper from "@mui/material/Paper";
import { useRef, useEffect, useState } from "react";

const matchups = [[1, 16],[2,15],[3,14],[4,13],[5,12],[6,11],[7,10],[8,9]]



    // round 1
    const [r1g1, setr1g1] = useState({team1:"W1",team2:"W16",value:"W1"});
    const [r1g2, setr1g2] = useState({team1:"W8",team2:"W9",value:"W8"});
    const [r1g3, setr1g3] = useState({team1:"W5",team2:"W12",value:"W4"});
    const [r1g4, setr1g4] = useState({team1:"W4",team2:"W13",value:"W5"});
    const [r1g5, setr1g5] = useState({team1:"W6",team2:"W11",value:"W6"});
    const [r1g6, setr1g6] = useState({team1:"W3",team2:"W14",value:"W3"});
    const [r1g7, setr1g7] = useState({team1:"W7",team2:"W10",value:"W7"});
    const [r1g8, setr1g8] = useState({team1:"W2",team2:"W15",value:"W2"});
    // round 2
    const [r2g1, setr2g1] = useState({team1:r1g1.value,team2:r1g2.value,value:r1g1.value});
    const [r2g2, setr2g2] = useState({team1:r1g3.value,team2:r1g4.value,value:r1g3.value});
    const [r2g3, setr2g3] = useState({team1:r1g5.value,team2:r1g6.value,value:r1g5.value});
    const [r2g4, setr2g4] = useState({team1:r1g7.value,team2:r1g8.value,value:r1g7.value});
    // round 3
    const [r3g1, setr3g1] = useState({team1:r2g1.value,team2:r2g2.value,value:r2g1.value});
    const [r3g2, setr3g2] = useState({team1:r2g3.value,team2:r2g4.value,value:r2g3.value});
    // round 4
    const [r4g1, setr4g1] = useState({team1:r3g1.value,team2:r3g2.value,value:r3g1.value});

export default function Bracket() {

  return (
      <Stack direction="row" spacing={4}>
        <Stack
          alignItems="center"
          justifyContent="center"
          spacing={2}
          sx={{ height: 1000 }}
        >
          <Game />
          <Game />
          <Game />
          <Game />
          <Game />
          <Game />
          <Game />
          <Game />
        </Stack>
        <Stack
          alignItems="center"
          justifyContent="center"
          spacing={16}
          sx={{ height: 1000 }}
        >
          <Game />
          <Game />
          <Game />
          <Game />
        </Stack>
        <Stack
          alignItems="center"
          justifyContent="center"
          spacing={47}
          sx={{ height: 1000 }}
        >
          <Game />
          <Game />
        </Stack>
        <Stack
          alignItems="center"
          justifyContent="center"
          sx={{ height: 1000 }}
        >
          <Game />
        </Stack>
      </Stack>
  );
}





<Stack direction="row" justifyContent='center' spacing={2.5}>
<Stack
  alignItems="center"
  justifyContent="center"
  spacing={2}
  sx={{ height: 800 }}
>
  {Array(8)
    .fill(0)
    .map((x, i) => {
      return renderGame(i);
    })}
</Stack>
<Stack
  alignItems="center"
  justifyContent="center"
  spacing={14}
  sx={{ height: 800 }}
>
  {Array(4)
    .fill(0)
    .map((x, i) => {
      return renderGame(i + 8 + 32);
    })}
</Stack>
<Stack
  alignItems="center"
  justifyContent="center"
  spacing={40}
  sx={{ height: 800 }}
>
  {Array(2)
    .fill(0)
    .map((x, i) => {
      return renderGame(i + 12);
    })}
</Stack>
<Stack alignItems="center" justifyContent="center" sx={{ height: 800 }}>
  {Array(1)
    .fill(0)
    .map((x, i) => {
      return renderGame(i + 14);
    })}
</Stack>

<Stack alignItems="center" justifyContent="center" sx={{ height: 800 }}>
  {Array(1)
    .fill(0)
    .map((x, i) => {
      return renderGame(i + 14 + 15);
    })}
</Stack>
<Stack
  alignItems="center"
  justifyContent="center"
  spacing={40}
  sx={{ height: 800 }}
>
  {Array(2)
    .fill(0)
    .map((x, i) => {
      return renderGame(i + 12 + 15);
    })}
</Stack>
<Stack
  alignItems="center"
  justifyContent="center"
  spacing={14}
  sx={{ height: 800 }}
>
  {Array(4)
    .fill(0)
    .map((x, i) => {
      return renderGame(i + 8 + 15);
    })}
</Stack>
<Stack
  alignItems="center"
  justifyContent="center"
  spacing={2}
  sx={{ height: 800 }}
>
  {Array(8)
    .fill(0)
    .map((x, i) => {
      return renderGame(i + 15);
    })}
</Stack>
</Stack>