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
import {useState} from "react";
import Divider from '@mui/material/Divider';
import { orange } from '@mui/material/colors';

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

export default function Game(props) {
    const team1_label = props.team1.concat(" (",Math.round(100*props.team1_w_prob).toString(),"%)")
    const team2_label = props.team2.concat(" (",Math.round(100*(1-props.team1_w_prob)).toString(),"%)")

  return (
    <Card variant="outlined" sx={{ width: 150, height: 90, bgcolor:orange['50']}}>
      <CardContent>
        {/*<Typography variant="body2">Expected points: {props.expected_points > 0 ? (props.expected_points).toFixed(2) : ""}</Typography>*/}
        <FormControl>
          <RadioGroup
            name="controlled-radio-buttons-group"
            value={props.value}
            onChange={props.handleChange}
          >
            <FormControlLabel value={props.team1} control={<Radio sx={{'& .MuiSvgIcon-root': {fontSize: 16}}}/>} label={<Typography variant="body2">{team1_label}</Typography>} />
            <Divider sx={{width:220}}/>
            <FormControlLabel value={props.team2} control={<Radio sx={{'& .MuiSvgIcon-root': {fontSize: 16}}}/>} label={<Typography variant="body2">{team2_label}</Typography>} />
          </RadioGroup>
        </FormControl>
      </CardContent>
    </Card>
  );
}
