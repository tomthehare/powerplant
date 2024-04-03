interface NavBarProps {
  title: string;
}

const NavBar = ({ title }: NavBarProps) => {
  return (
    <>
      <div className="rowBlock navBar">
        <h1>{title}</h1>
      </div>
    </>
  );
};

export default NavBar;
