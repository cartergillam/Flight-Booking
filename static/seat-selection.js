let isRoundTrip = false;
let departureSeat = null;
let returnSeat = null;
const seatGrid = document.querySelector('.seat-grid');
const seatSections = [
    ['A', 'B', 'C'],  // First section
    ['D', 'E', 'F'],  // Middle section
    ['G', 'H', 'I']   // Last section
];
const rows = 7;  // Total rows

function createSeatGrid(gridId) {
    const seatGrid = document.getElementById(gridId);
    seatGrid.innerHTML = '';
    for (let i = 1; i <= rows; i++) {
        seatSections.forEach((section, sectionIndex) => {
            section.forEach(seatLetter => {
                createSeat(seatGrid, i, seatLetter);
            });
            if (sectionIndex < seatSections.length - 1) {
                createRowNumber(seatGrid, i);
            }
        });
    }
}

function createSeat(grid, row, letter) {
    const seat = document.createElement('div');
    seat.classList.add('seat');
    seat.dataset.row = row;
    seat.dataset.col = letter;
    if (Math.random() > 0.3) {
        seat.classList.add('seat-available');
        seat.textContent = letter;
    } else {
        seat.classList.add('seat-unavailable');
        seat.textContent = 'X';
    }
    grid.appendChild(seat);
}

function createRowNumber(grid, number) {
    const rowNumber = document.createElement('div');
    rowNumber.classList.add('row-number');
    rowNumber.textContent = number;
    grid.appendChild(rowNumber);
}

function updateSeatSelection(seat, gridId) {
    const seatId = `${seat.getAttribute('data-row')}${seat.getAttribute('data-col')}`;
    if (gridId === 'departureSeatGrid') {
        departureSeat = seatId;
        document.getElementById('departureSeatSelection').textContent = seatId;
    } else {
        returnSeat = seatId;
        document.getElementById('returnSeatSelection').textContent = seatId;
    }
}

document.querySelectorAll('.seat-grid').forEach(grid => {
    grid.addEventListener('click', (e) => {
        if (e.target.classList.contains('seat-available')) {
            const selectedSeat = grid.querySelector('.seat-selected');
            if (selectedSeat) {
                selectedSeat.classList.remove('seat-selected');
                selectedSeat.classList.add('seat-available');
            }
            e.target.classList.remove('seat-available');
            e.target.classList.add('seat-selected');
            updateSeatSelection(e.target, grid.id);
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    fetch('/get-trip-info')
        .then(response => response.json())
        .then(data => {
            isRoundTrip = data.isRoundTrip;
            document.getElementById('passengerName').textContent = data.passengerName;
            if (!isRoundTrip) {
                document.getElementById('returnBtn').style.display = 'none';
                document.getElementById('returnInfo').style.display = 'none';
                document.getElementById('returnSeatGrid').style.display = 'none';
            }
            createSeatGrid('departureSeatGrid');
            if (isRoundTrip) {
                createSeatGrid('returnSeatGrid');
            }
        });

    document.getElementById('departureBtn').addEventListener('click', () => {
        switchGrid('departure');
    });

    document.getElementById('returnBtn').addEventListener('click', () => {
        if (isRoundTrip) {
            switchGrid('return');
        }
    });
});

function switchGrid(type) {
    if (type === 'departure') {
        document.getElementById('departureSeatGrid').style.display = 'grid';
        document.getElementById('returnSeatGrid').style.display = 'none';
        document.getElementById('departureBtn').classList.add('active');
        document.getElementById('returnBtn').classList.remove('active');
    } else {
        document.getElementById('departureSeatGrid').style.display = 'none';
        document.getElementById('returnSeatGrid').style.display = 'grid';
        document.getElementById('departureBtn').classList.remove('active');
        document.getElementById('returnBtn').classList.add('active');
    }
}

document.getElementById('proceed-button').addEventListener('click', () => {
    if (!departureSeat || (isRoundTrip && !returnSeat)) {
        alert('Please select seats for all flights.');
        return;
    }
    fetch('/save-seat-selection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            departureSeat: departureSeat,
            returnSeat: isRoundTrip ? returnSeat : null
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/profile/' + encodeURIComponent(data.userEmail);
        } else {
            alert('Error saving seat selection. Please try again.');
        }
    });
});

document.getElementById('back-button').addEventListener('click', () => {
    window.location.href = '/';
});