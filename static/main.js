const usernameContainer = document.getElementById("profileUsernameCnt");

async function getUser() {
    const response = await fetch("/api/dashboard");
    if (!response.ok){
        console.log("Authentication failed");
        return;
    }
    const data = await response.json();

    if (usernameContainer) usernameContainer.textContent = data.username
}

getUser()

async function loginUserBtn() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorLog = document.getElementById("error");
    const response = await fetch("/api/login", {
        method: "POST",
        headers: {
            "content-type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    const data = await response.json()

    if (response.ok) {
        console.log("LOgin Successful")
        window.location.href = "/dashboard"
    }
    else{
        let error = data.error
        let loginerror = data.loginAlert
        if(error){
            errorLog.textContent = error;
        }
        if(loginerror){
            errorLog.textContent = loginerror
        }
        
    }
}

async function RegisterUserBtn() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorLog = document.getElementById("error");
    const response = await fetch("/api/register", {
        method: "POST",
        headers: {
            "content-type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    }
    );
    let data = await response.json()
    console.log("error:", data)
    if(response.ok){
        window.location.href = "/dashboard"
    }else{
        const error = data.error;
        const message = data.message;
        if (error) {
            errorLog.textContent = error;
        }
        if (message) {
            errorLog.textContent = message;
        }
        
    }
}

async function getProjects() {
    const projectDataContainer = document.getElementById("projectDataContainer");
    if (!projectDataContainer) return;
    const response = await fetch("/api/projects");
    const projects = await response.json();
    const errormsg = projects.error;
    if(errormsg){
        console.log("error:", errormsg)
    }
    else{
        projects.forEach(project => {
        projectDataContainer.innerHTML += `<div class="projectContainer" id="projectId${project.projectId}">

        <div class="projectsinContainer">
        <p>${project.projectName}</p>
        </div>
        <p class="projectLevelContainer">Level: ${project.projectLevel}
        

        <div id="projectNav-${project.projectId}" class="projectNavigation">

            <button class="projectNavigations" id="projectNavEdit-${project.projectId}" onclick="editPage(${project.projectId})">Edit</button>

            <button id="projectDelBtn" class="projectNavigations" id="projectNavDelete-${project.projectId}" delete_btn-id=${project.projectId} onclick="deleteProject(${project.projectId})">Delete</button>

        </div>
</div>`;
        });
    }
    
}

getProjects()

async function AddProject() {
    const text = document.getElementById("text").value;
    const difficulty = document.getElementById("difficulty").value;
    const AddProjectPageErrorHandler = document.getElementById("AddProjectPageErrorHandler");
    const response = await fetch("/api/add", {
        method: "POST",
        headers: {
            "content-type": "application/json"
        },
        body: JSON.stringify({
            devCntName: text,
            devcntlvl: difficulty
        })
    })
    const data = await response.json();
    const errormsg = data.error;
    const successmsg = data.mmessage

    if(errormsg){
        console.log("error:", errormsg)
        AddProjectPageErrorHandler.textContent = errormsg;
    }
    if(successmsg){
        console.log("success", successmsg)
        AddProjectPageErrorHandler.textContent = successmsg;
        window.location.href = "/dashboard"
    }
}

function editPage(id) {
    console.log("id", id)
    window.location.href = `/edit/${id}`
}

async function editProject() {
    const name = document.getElementById("contentNameToEdit").value;
    const level = document.getElementById("projectLvlToEdit").value;
    const ErrorLogEditPage = document.getElementById("ErrorLogEditPage")
    const saveBtn = document.getElementById("editsSaveBtn")
    const id = saveBtn.getAttribute("project-id")
    const response = await fetch(`/api/dashboard/projects/edit/${id}`, {
        method: "PATCH",
        headers: {
            "content-type": "application/json"
        }, 
        body: JSON.stringify({
            "devCntName": name,
            "devcntlvl": level
        })
    })
    const data = await response.json()
    const error = data.error;
    const message = data.message;
    if(error){
        console.log("Error")
        console.log("Status code", response.status, "data", data)
        ErrorLogEditPage.textContent = error
    }
    else if (data){
        window.location.href = "/dashboard"
    }
     
}

async function deleteProject(id) {
    const response = await fetch(`/api/dashboard/projects/delete/${id}`, {
        method: "DELETE", credentials: "include"
    })
    const data = response.json()
    error = data.error;
    success = data.message;
    if (error){
        console.log("error: ", data)
    }
    if (success){
      
    }
    window.location.href = "/dashboard"

}