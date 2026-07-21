import { Link } from 'react-router-dom';

export function Logo() {
  return (
    <Link to="/dashboard" className="flex items-center select-none">
      <h1
        className="text-xl sm:text-2xl font-bold tracking-widest leading-none text-left font-montserrat"
      >
        <div className="text-white">P2P</div>
        <div className="text-white">CORPUS</div>
      </h1>
    </Link>
  );
}

export default Logo;
