// docs/source/_static/custom.js
document.addEventListener("DOMContentLoaded", function() {
    var header = document.querySelector(".wy-side-nav-search");
    if (header) {
        var githubLink = document.createElement("a");
        githubLink.href = "https://github.com/LSSTDESC/Smokescreen";
        githubLink.target = "_blank";
        githubLink.style.display = "flex";
        githubLink.style.alignItems = "center";
        githubLink.style.marginLeft = "10px";
        githubLink.style.marginTop = "12px"; // Add vertical space

        var githubIcon = document.createElement("i");
        githubIcon.className = "fab fa-github";
        githubIcon.style.fontSize = "20px";

        var githubText = document.createElement("span");
        githubText.textContent = "DESC Smokescreen Repository";
        githubText.style.marginLeft = "10px";
        githubText.style.fontSize = "15px";

        githubLink.appendChild(githubIcon);
        githubLink.appendChild(githubText);
        header.appendChild(githubLink);
    }
});