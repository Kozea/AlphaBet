drop table if exists user_bets;
drop table if exists users;

create table users
(
  u_id integer primary key autoincrement,
  username varchar(20) not null,
  password varchar(20) not null
);

create table user_bets
(
  id_bet integer primary key autoincrement,
  u_id integer not null,
  match_id integer not null,
  outcome varchar(1),
  FOREIGN KEY (u_id) REFERENCES users(u_id),
  CONSTRAINT couple_unique UNIQUE (u_id, match_id)
);

INSERT INTO users (username, password) 
VALUES 
('Romain', 'Rouvier'),
('Guillaume', 'Ayoub'),
('Maelle', 'Pinto'),
('John Doe', 'lemotdepasse'); 
