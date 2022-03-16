import * as React from "react";
import { ArcherContainer, ArcherElement } from "react-archer";
import Connector from "react-svg-connector";

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
import MiniBracket from '../components/minibracket.js';

const matchups = [[1, 16],[2,15],[3,14],[4,13],[5,12],[6,11],[7,10],[8,9]]


export default function Bracket() {
    const [expectedPoints, setExpectedPoints] = useState(0);

  return (
    <Container>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" align="center" component="h1" gutterBottom>
          Create Bracket
        </Typography>
      </Box>
      <Box sx={{ my: 4}}>
          <Typography variant="h6" align="center">Total Expected Points: {expectedPoints.toFixed(2)}</Typography>
          <Typography variant="h6" align="center">Difference from People's Bracket: 5%</Typography>
          
      </Box>
      <MiniBracket setExpectedPoints={setExpectedPoints}/>
      <Copyright />
    </Container>
  );
}
