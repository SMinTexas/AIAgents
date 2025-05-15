import React from "react";
import NewHome from "./pages/NewHome";
import "leaflet/dist/leaflet.css";

window.onerror = function (message, source, lineno, colno, error) {
  console.error("Global Error Caught:", message, "at", source, "line", lineno, "column", colno, error);
}

window.addEventListener("beforeunload", (event) => {
  console.log("Page is reloading!");
});

const App = () => {
  return (
    <div>
      <NewHome />
    </div>
  );
};

export default App;
