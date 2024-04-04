interface NavBarProps {
  title: string;
}

const NavBar = ({ title }: NavBarProps) => {
  return (
    <>
      <nav className="navbar navbar-expand-md navbar-dark mt-2 mb-0">
        <span className="navbar-brand fw-bold fs-2">{title}</span>
      </nav>
    </>
  );
};

export default NavBar;
