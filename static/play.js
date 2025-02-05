let startTime;
let running = false;
let timer;
let dayofweek;
let dayofweekint;
let weekNames = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
let year;
let month;
let day;
let elapsedTime;
let hide = false;
let milliseconds = 0;
let seconds = 0;

function play() {

    if (!running) {
        running = true;
        startTime = Date.now();
        timer = setInterval(updateTimer, 1); // Update every millisecond
    }
    else if (running) {
        return;
    }

    for (let i = 0; i < 7; i++) {
        const button = document.getElementById(weekNames[i]);
        button.classList.remove('btn-success', 'btn-danger');
    }

    year = Math.floor(Math.random() * (2200 - 1800)) + 1800;

    // Generate a random month (1 to 12)
    month = Math.floor(Math.random() * 12 + 1);

    const months31 = [1,3,5,7,8,10,12] // Months with 31 days
    const months30 = [4,6,9,11] // Month with 30 days

    // Check for leap year
    if (month == 2) {
        if (year % 4 == 0) {
            if (year % 400 == 0) {
                day = Math.floor(Math.random() * 29) + 1;
            }
            else if (year % 100 == 0) {
                day = Math.floor(Math.random() * 28) + 1;
            }
            else {
                day = Math.floor(Math.random() * 29) + 1;
            }
        }
        else {
            day = Math.floor(Math.random() * 28) + 1;
        }
    }
    else if (months31.includes(month)) {
        day = Math.floor(Math.random() * 31) + 1;
    }
    else if (months30.includes(month)) {
        day = Math.floor(Math.random() * 30) + 1;
    }

    // Date object
    let randomDate = new Date(year, month-1, day);

    // Array of months
    const monthNames = ["January", "February", "March", "April", "May", "June", 
                        "July", "August", "September", "October", "November", "December"];

    // Format for button
    let formattedDate = `${randomDate.getDate()} ${monthNames[month-1]} ${randomDate.getFullYear()}`;

    // Change the button text to the formatted date
    button = document.getElementById("playbutton");
    button.textContent = formattedDate;

    // Change button colour
    button.classList.remove("btn-primary");
    button.classList.add("btn-secondary");

    // Also return the day of week of that day
    dayofweekint = randomDate.getDay();
    dayofweek = weekNames[dayofweekint];
}

function check(x) {

    if (running) {
            clearInterval(timer);
            running = false;

            // Sending data to backend
            const myHeaders = new Headers();
            myHeaders.append("Content-Type", "application/json");

            const response = fetch("/submit", {
                method: "POST",
                body: JSON.stringify({ timer: elapsedTime, year: year, month: month, day: day, dayofweek: dayofweekint, answer: x}),
                headers: myHeaders,
            });
    }

    datebutton = document.getElementById(weekNames[x]);
    // If answer is correct
    if (x == dayofweekint) {
        datebutton.classList.add("btn-success");
    }
    // If answer is not correct
    else {
        datebutton.classList.add("btn-danger");
    }
}

function updateTimer() {
    elapsedTime = Date.now() - startTime;
    milliseconds = Math.floor((elapsedTime % 1000));
    seconds = Math.floor((elapsedTime / 1000));

    if (hide == false) {
        document.getElementById("timer").textContent = 
        `${String(seconds)}.${String(milliseconds).padStart(3, '0')}`;
    }
    else {
        document.getElementById("timer").textContent = "";
    }
    
} 

function hidetext(){
    if (hide == false) {
        hide = true;
        if (running == false) {
            document.getElementById("timer").textContent = "";
        }
    }
    else {
        hide = false;
        if (running == false) {
            document.getElementById("timer").textContent = 
            `${String(seconds)}.${String(milliseconds).padStart(3, '0')}`;
        }
    }
}