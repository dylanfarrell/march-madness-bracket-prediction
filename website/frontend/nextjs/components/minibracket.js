import * as React from "react";
import Stack from "@mui/material/Stack";
import Typography from '@mui/material/Typography';
import Game from "./game";
import { useEffect, useState } from "react";
import win_probs from "./win_probs";

const scoring = {
  1: 320 / 32,
  2: 320 / 16,
  3: 320 / 8,
  4: 320 / 4,
  5: 320 / 2,
  6: 320 / 1,
};

let teams = [];

const regions = ["West", "South", "East", "North"];

regions.forEach((region) => {
  for (let i = 1; i <= 16; i++) {
    teams.push(i.toString().concat(" ", region));
  }
});

let matchups = [];

regions.forEach((region) => {
  matchups.push(["1 ".concat(region), "16 ".concat(region)]);
  matchups.push(["8 ".concat(region), "9 ".concat(region)]);
  matchups.push(["5 ".concat(region), "12 ".concat(region)]);
  matchups.push(["4 ".concat(region), "13 ".concat(region)]);
  matchups.push(["6 ".concat(region), "11 ".concat(region)]);
  matchups.push(["3 ".concat(region), "14 ".concat(region)]);
  matchups.push(["7 ".concat(region), "10 ".concat(region)]);
  matchups.push(["2 ".concat(region), "15 ".concat(region)]);
});

const blank = "_________";

const default_game = {
  team1: blank,
  team2: blank,
  team1_p_prob: null,
  team2_p_prob: null,
  team1_w_prob: 0.5,
  team2_w_prob: 0.5,
  value: null,
  expected_points: 0,
};

const games_before_round = {
  1: 0,
  2: 32,
  3: 48,
  4: 56,
  5: 60,
  6: 62,
};

export default function MiniBracket(props) {
  let games = Array(matchups.length * 2 - 1);
  for (let i = 0; i < 32; i++) {
    games[i] = useState({
      team1: matchups[i][0],
      team2: matchups[i][1],
      team1_p_prob: 1,
      team2_p_prob: 1,
      team1_w_prob: win_probs[matchups[i][0].concat(", ", matchups[i][1])],
      team2_w_prob: 1 - win_probs[matchups[i][0].concat(", ", matchups[i][1])],
      value: null,
      expected_points: 0,
      round: 1,
    });
  }

  for (let i = 32; i < 48; i++) {
    games[i] = useState({ ...default_game, round: 2 });
  }

  for (let i = 48; i < 56; i++) {
    games[i] = useState({ ...default_game, round: 3 });
  }

  for (let i = 56; i < 60; i++) {
    games[i] = useState({ ...default_game, round: 4 });
  }

  for (let i = 60; i < 62; i++) {
    games[i] = useState({ ...default_game, round: 5 });
  }

  games[62] = useState({ ...default_game, round: 6 });

  // move into the game use effects
  useEffect(() => {
    const total = 0;
    games.forEach((game) => {
      total += game[0].expected_points;
    });
    props.setExpectedPoints(total);
  });

  const getParents = (game) => {
    const round = games[game][0].round;
    const idx = game - games_before_round[round];
    const t1_parent_idx = 2 * idx + games_before_round[round - 1];
    const t2_parent_idx = 2 * idx + 1 + games_before_round[round - 1];
    return [games[t1_parent_idx][0], games[t2_parent_idx][0]];
  };

  const update = (game) => {
    const [t1_parent, t2_parent] = getParents(game);
    const new_team1 = t1_parent.value || blank;
    const new_team2 = t2_parent.value || blank;
    const new_team1_p_prob =
      t1_parent.value == t1_parent.team1
        ? t1_parent.team1_p_prob * t1_parent.team1_w_prob
        : t1_parent.team2_p_prob * t1_parent.team2_w_prob;
    const new_team2_p_prob =
      t2_parent.value == t2_parent.team1
        ? t2_parent.team1_p_prob * t2_parent.team1_w_prob
        : t2_parent.team2_p_prob * t2_parent.team2_w_prob;
    const new_team1_w_prob =
      win_probs[(t1_parent.value || "").concat(", ", t2_parent.value || "")] ||
      0.5;
    const new_team2_w_prob = 1 - new_team1_w_prob;
    const new_value =
      games[game][0].value == new_team1 || games[game][0].value == new_team2
        ? games[game][0].value
        : null;
    const new_expected_points = new_value
      ? new_value == new_team1
        ? new_team1_w_prob * scoring[games[game][0].round] * new_team1_p_prob
        : new_team2_w_prob * scoring[games[game][0].round] * new_team2_p_prob
      : 0;

    games[game][1]((state) => ({
      ...state,
      team1: new_team1,
      team2: new_team2,
      team1_p_prob: new_team1_p_prob,
      team2_p_prob: new_team2_p_prob,
      team1_w_prob: new_team1_w_prob,
      team2_w_prob: new_team2_w_prob,
      value: new_value,
      expected_points: new_expected_points,
    }));
  };

  for (let i = 32; i < games.length; i++) {
    useEffect(() => {
      update(i);
    }, getParents(i));
  }

  const handleChange = (game) => (event) => {
    let w_prob = 0.5;
    if (event.target.value == games[game][0].team1) {
      w_prob = games[game][0].team1_w_prob * games[game][0].team1_p_prob;
    } else {
      w_prob = games[game][0].team2_w_prob * games[game][0].team2_p_prob;
    }
    games[game][1]((state) => ({
      ...state,
      value: event.target.value,
      expected_points: w_prob * scoring[state.round],
    }));
  };

  const renderGame = (i) => {
    return (
      <Game
        key={i}
        {...games[i][0]}
        handleChange={(event) => handleChange(i)(event)}
      />
    );
  };

  const renderRound = (n, start, spacing) => {
    let rows = [];
    for (let i = start; i < start + n; i++) {
      rows.push(renderGame(i));
    }
    return (
      <Stack
        alignItems="center"
        justifyContent="center"
        spacing={spacing}
        sx={{ height: 800 }}
      >
        {rows}
      </Stack>
    );
  };

  const round_spacing = {
    1: 2,
    2: 14,
    3: 40,
    4: 1,
  };
  const games_in_round = {
    1: 8,
    2: 4,
    3: 2,
    4: 1,
  };
  const renderRegion = (region, direction) => {
    let rows = [];
    for (let i = 1; i <= 4; i++) {
      rows.push(
        renderRound(
          games_in_round[i],
          games_before_round[i] + region * games_in_round[i],
          round_spacing[i]
        )
      );
    }
    return (
      <Stack direction={direction} justifyContent="center" spacing={2.5}>
        {rows}
      </Stack>
    );
  };

  return (
    <Stack alignItems="center" spacing={1}>
      <Stack direction="row" spacing = {2}>
        {renderRegion(0, "row")}
        {renderRegion(2, "row-reverse")}
      </Stack>
    <Stack direction="row" alignItems='center' spacing = {2}>
        {renderRound(1,60,2)}
        {renderGame(62)}
        {renderRound(1,61,2)}
    </Stack>
      <Stack direction="row" spacing = {2}>
        {renderRegion(1, "row")}
        {renderRegion(3, "row-reverse")}
      </Stack>
    </Stack>
  );
}
