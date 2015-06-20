CREATE TABLE log (
    channel TEXT,
    datetime INTEGER,
    user TEXT,
    message TEXT
);

CREATE INDEX user_index ON log(user);
CREATE INDEX message_index ON log(message);
