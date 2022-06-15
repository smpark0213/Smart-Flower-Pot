function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 0 - 제자리 // 1 - 오른쪽 // -1 - 왼쪽
function check_move_direction(curr_plant, target_plant) {
    if (curr_plant === target_plant) {
        return 0;
    }
    else if (curr_plant === 0) {
        return 1;
    }
    else if (curr_plant === 1) {
        if (target_plant === 0) {
            return -1;
        }
        else {
            return 1;
        }
    }
    else if (curr_plant === 2) {
        return -1;
    }
}


module.exports = {
    sleep,
    check_move_direction
}