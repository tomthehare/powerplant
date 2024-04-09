import { Outlet } from "react-router-dom";
import NavBar from "../components/NavBar";

const MainLayout = () => {
  return (
    <>
      <NavBar
        title="powerPLANT"
        onLiveButtonClick={() => console.log("live")}
        onConfigButtonClick={() => console.log("config")}
      />
      <Outlet />
    </>
  );
};

export default MainLayout;
