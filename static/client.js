// WebSocket connection
var connection = null;

// Initial View Loading
window.onload = function () {
    // localStorage.clear()
    // check if the token exists - if it does, open profile view, if not open welcome view
    if (localStorage.getItem("token") == null) {
        localStorage.removeItem("token");
        welcomeView();
    } else {
        profileView();
    }
};

/**
 * Functions for changing views
 */

welcomeView = function () {
    document.getElementById("currentView").innerHTML = document.getElementById('welcomeView').innerHTML;
};

profileView = function () {
    // show the profile view
    document.getElementById("currentView").innerHTML = document.getElementById('profileView').innerHTML;
    // display chart
    displayChart("all", null);

    var request = new XMLHttpRequest();
    request.open("GET", "/get_user_data_by_token/" + localStorage.getItem("token"), true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            personalInformation(JSON.parse(request.responseText)["data"]);
            if (connection === null) {
                webSocket_handler(JSON.parse(request.responseText)["data"][0]);
            }
            reloadWall('home');
        }
    };
    request.setRequestHeader("Content-Type", "application/json");
    request.send(null);
};

searchView = function () {
    document.getElementById("currentView").innerHTML = document.getElementById('searchView').innerHTML;
};

accountView = function () {
    document.getElementById("currentView").innerHTML = document.getElementById('accountView').innerHTML;
    showProfilePicture();
};

/**
 * Functions for displaying information on the views
 */

personalInformation = function (info) {
    document.getElementById("infoEmail").innerHTML = info[0];
    document.getElementById("infoFirstName").innerHTML = info[1];
    document.getElementById("infoFamilyName").innerHTML = info[2];
    document.getElementById("infoGender").innerHTML = info[3];
    document.getElementById("infoCity").innerHTML = info[4];
    document.getElementById("infoCountry").innerHTML = info[5];
    document.getElementById("profilePicture").src = info[6];
};

var chartDataSet = [];
displayChart = function (fields, data) {
    if (fields === "all") {
        // On initial profile view loading, hold all the chart information from database
        var request = new XMLHttpRequest();
        request.open("GET", "/get_chart_data/" + localStorage.getItem("token"), true);
        request.onreadystatechange = function () {
            if (request.readyState === 4 && request.status === 200) {
                chartDataSet = JSON.parse(request.responseText)["data"]
                //show the chart
                new Chart(document.getElementById("myChart"), {
                    type: 'doughnut',
                    data: {
                        labels: ["Messages", "Users online", "Profile Views"],
                        datasets: [
                            {
                                backgroundColor: ["#3e95cd", "#3cba9f", "#c45850"],
                                data: chartDataSet
                            }
                        ]
                    },
                    options: {}
                });
            }
        };
        request.send(null);
    } else {
        // Update only the fields needed
        switch (fields) {
            case "messages":
                chartDataSet[0] = data;
                break;
            case "users_online":
                chartDataSet[1] = data;
                break;
            case "profile_views":
                chartDataSet[2] = data;
                break;
            default:
                break;
        }
        new Chart(document.getElementById("myChart"), {
            type: 'doughnut',
            data: {
                labels: ["Messages", "Users online", "Profile Views"],
                datasets: [
                    {
                        backgroundColor: ["#3e95cd", "#3cba9f", "#c45850"],
                        data: chartDataSet
                    }
                ]
            },
            options: {}
        });
    }
};

showProfilePicture = function () {
    var request = new XMLHttpRequest();
    request.open("GET", "/get_profile_picture/" + localStorage.getItem("token"), true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            document.getElementById("profilePicture").src = JSON.parse(request.responseText)["data"];
        } else {
            document.getElementById("profilePicture").src = "/get_media/users/default-user.png"
        }
    };
    request.send(null);
};

reloadWall = function (location) {
    var messages = "";
    var request = new XMLHttpRequest();
    var token = localStorage.getItem("token");
    if (location === 'home') {
        request.open("GET", "/get_user_messages_by_token/" + token, true);
    } else {
        var email = document.getElementById("infoEmail").innerHTML;
        request.open("GET", "/get_user_messages_by_email/" + email + "/" + token, true);
    }
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            messages = JSON.parse(request.responseText)["data"];
            var messageString = "";
            for (var i = 0; i < messages.length; i++) {
                if (messages[i][1] === "text") {
                    messageString += "<p><b>" + messages[i][0] + ":</b><span draggable='true' ondragstart='drag(event)'> " + messages[i][2] + "</span></p>";
                } else {
                    var videoHtml = '<video width="320" height="240" controls><source src="' + messages[i][2] + '" type="video/mp4"></video>';
                    messageString += "<p><b>" + messages[i][0] + ":</b> " + videoHtml + "</p>";
                }
            }
            document.getElementById(location + 'MessageWall').innerHTML = messageString;
        }
    };
    request.send(null);
};

/**
 * Form functions
 */

signIn = function (form, email, password) {
    var socketEmail;
    var data = {};
    if (form !== null) {
        socketEmail = form.inputEmail.value;
        data.email = form.inputEmail.value;
        data.password = form.inputPassword.value;
    } else {
        socketEmail = email;
        data.email = email;
        data.password = password;
    }

    var request = new XMLHttpRequest();
    request.open("POST", "/sign_in", true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            webSocket_handler(socketEmail);
            localStorage.setItem("token", JSON.parse(request.responseText)["data"]);
            profileView();
        } else {
            document.getElementById("signInFeedback").innerHTML = JSON.parse(request.responseText)["message"];
        }
    };
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(data));

    return false;
};

signUp = function (form) {
    var signUpInfo = {};
    signUpInfo["firstname"] = form.firstName.value;
    signUpInfo["familyname"] = form.familyName.value;
    signUpInfo["city"] = form.city.value;
    signUpInfo["country"] = form.country.value;
    signUpInfo["gender"] = form.gender.value;
    signUpInfo["email"] = form.signupEmail.value;

    var signupPassword = form.signupPassword.value;
    var signupRepeatPassword = form.signupRepeatPassword.value;
    if (signupPassword.length < 5) {
        document.getElementById("signUpFeedback").innerHTML = "Password must be at least 5 characters long.";
        return false;
    }
    if (signupPassword !== signupRepeatPassword) {
        document.getElementById("signUpFeedback").innerHTML = "Passwords don't match.";
        return false;
    }
    signUpInfo["password"] = signupPassword;

    var request = new XMLHttpRequest();
    request.open("POST", "/sign_up", true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            signIn(null, signUpInfo["email"], signUpInfo["password"]);
        } else {
            document.getElementById("signUpFeedback").innerHTML = JSON.parse(request.responseText)["message"];
        }
    };
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(signUpInfo));

    return false;
};

signOut = function () {
    var data = {};
    data["token"] = localStorage.getItem("token");

    var request = new XMLHttpRequest();
    request.open("POST", "/sign_out", true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            localStorage.removeItem("token");
            welcomeView();
        }
    };
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(data));
};

changePassword = function (form) {
    var newPassword = form.newPassword.value;
    var newPasswordRepeat = form.newPasswordRepeat.value;
    if (newPassword.length < 5) {
        document.getElementById("passwordChangeFeedback").innerHTML = "New password is too short.";
        return false;
    }
    if (newPassword !== newPasswordRepeat) {
        document.getElementById("passwordChangeFeedback").innerHTML = "New passwords don't match.";
        return false;
    }

    var data = {};
    data["oldPassword"] = form.oldPassword.value;
    data["newPassword"] = form.newPassword.value;
    data["token"] = localStorage.getItem("token");

    var request = new XMLHttpRequest();
    request.open("POST", "/change_password", true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            document.getElementById("oldPassword").value = "";
            document.getElementById("newPassword").value = "";
            document.getElementById("newPasswordRepeat").value = "";
            document.getElementById("passwordChangeFeedback").style.color = "green";
            document.getElementById("passwordChangeFeedback").innerHTML = JSON.parse(request.responseText)["message"];
            form.reset();
        } else {
            document.getElementById("passwordChangeFeedback").innerHTML = JSON.parse(request.responseText)["message"];
        }
    };
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(data));

    return false;
};

findUser = function (form) {
    var request = new XMLHttpRequest();
    request.open("GET", "/get_user_data_by_email/" + form.searchUser.value + "/" + localStorage.getItem("token"), true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            document.getElementById("userFound").style.visibility = "visible";
            document.getElementById("searchUserFeedback").innerHTML = "";
            personalInformation(JSON.parse(request.responseText)["data"]);
            reloadWall('user');
        } else {
            document.getElementById("userFound").style.visibility = "hidden";
            document.getElementById("searchUserFeedback").innerHTML = JSON.parse(request.responseText)["message"];
        }
    };
    request.send(null);

    return false;
};

postNewMessage = function (form, location) {
    var data = {};
    data["token"] = localStorage.getItem("token");
    data["email"] = document.getElementById("infoEmail").innerHTML;
    data["message"] = form.postMessage.value;

    var request = new XMLHttpRequest();
    request.open("POST", "/post_message", true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            reloadWall(location);
            document.getElementById("postMessage").value = "";
            form.reset();
        }
    };
    request.setRequestHeader("Content-Type", "application/json");
    request.send(JSON.stringify(data));

    return false;
};

postNewVideoMessage = function (form, location) {
    var formData = new FormData();
    formData.append("token", localStorage.getItem("token"));
    formData.append("email", document.getElementById("infoEmail").innerHTML);
    formData.append("type", form.videoFile.files[0].type);
    formData.append("video", form.videoFile.files[0]);

    var request = new XMLHttpRequest();
    request.open("POST", "/post_video_message", true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            reloadWall(location);
            document.getElementById("postVideoMessage").files = null;
        }
    };
    request.send(formData);

    return false;
};

changeProfilePicture = function (form) {
    var formData = new FormData();
    formData.append('token', localStorage.getItem("token"));
    formData.append('type', form.profilePicFile.files[0].type);
    formData.append('picture', form.profilePicFile.files[0]);

    var request = new XMLHttpRequest();
    request.open("POST", "/change_picture", true);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            document.getElementById("profilePicture").src = JSON.parse(request.responseText)["data"];
        }
    };
    request.send(formData);

    return false;
};

/**
 * Handler for the socket and interaction events
 */

webSocket_handler = function (email) {
    connection = new WebSocket("ws://" + window.location.hostname + ":5000/api");
    connection.onopen = function () {
        connection.send(email);
    };
    connection.onmessage = function (msg) {
        if (msg.data === "SIGN OUT") {
            localStorage.removeItem("token");
            welcomeView();
        }
        try {
            var jsonData = JSON.parse(msg.data);
            if (jsonData["message"] === "Chart Data") {
                displayChart(jsonData["field"], jsonData["data"]);
            }
        } catch (e) {}
    };
};

/**
 * Functions for drag-and-drop
 */

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.textContent);
}

function drop(ev) {
    ev.preventDefault();
    ev.target.value = ev.dataTransfer.getData("text");
}
