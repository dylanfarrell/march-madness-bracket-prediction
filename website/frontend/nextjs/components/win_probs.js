

const teams1 = [
    "1 Gonzaga",
    "16 Norfolk St",
    "8 Oklahoma",
    "9 Missouri",
    "5 Creighton",
    "12 UCSB",
    "4 Virgina",
    "13 Ohio",
    "6 USC",
    "11 Drake",
    "3 Kansas",
    "14 E Washington",
    "7 Oregon",
    "10 VCU",
    "2 Iowa",
    "15 GCU"
]

let teams = []

const regions = ['West','East','North','South'];

regions.forEach(region => {
    for (let i = 1; i <= 16; i++){
        teams.push((i.toString()).concat(' ',region))
    }
});

//console.log(teams)

let win_probs = {}
for (let i = 0; i < teams.length-1; i++) {
    for (let j = i+1; j < teams.length; j++){
        win_probs[teams[i].concat(', ', teams[j])] = Math.random()
    }
};


export default win_probs