import { Link } from "react-router-dom";

interface NavBarProps {
  title: string;
  onLiveButtonClick: () => void;
  onConfigButtonClick: () => void;
}

const NavBar = ({
  title,
  onLiveButtonClick,
  onConfigButtonClick,
}: NavBarProps) => {
  return (
    <>
      <nav className="navbar navbar-expand-md navbar-dark mt-2 mb-0">
        <span className="navbar-brand fw-bold fs-2">{title}</span>
        {/* I cant get this float to work right. */}
        <div className="float-right">
          <Link
            to="/"
            className="btn btn-secondary m-1"
            onClick={onLiveButtonClick}
          >
            Live
          </Link>
          <Link
            to="/config"
            className="btn btn-secondary m-1"
            onClick={onConfigButtonClick}
          >
            Config
          </Link>
        </div>
      </nav>
    </>
  );
};

export default NavBar;
