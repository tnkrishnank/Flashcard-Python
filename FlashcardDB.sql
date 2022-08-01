CREATE TABLE "uDetails" (
	"uID" INTEGER,
	"fName" TEXT NOT NULL,
	"pwd" TEXT NOT NULL,
	"enKey" TEXT NOT NULL,
	"lastVisited" TEXT NOT NULL,

	PRIMARY KEY("uID")
);

CREATE TABLE "uName" (
	"uID" INTEGER,
	"username" TEXT NOT NULL UNIQUE,

	PRIMARY KEY("uID"),
	FOREIGN KEY("uID") REFERENCES "uDetails"("uID") ON DELETE CASCADE
);

CREATE TABLE "uEmail" (
	"uID" INTEGER,
	"email" TEXT NOT NULL UNIQUE,

	PRIMARY KEY("uID"),
	FOREIGN KEY("uID") REFERENCES "uDetails"("uID") ON DELETE CASCADE
);

CREATE TABLE "uDeck" (
	"uID" INTEGER,
	"dID" INTEGER UNIQUE,
	"dName" TEXT NOT NULL,

	PRIMARY KEY("uID", "dID"),
	FOREIGN KEY("uID") REFERENCES "uDetails"("uID") ON DELETE CASCADE
);

CREATE TABLE "qDeck" (
	"qID" INTEGER,
	"dID" INTEGER NOT NULL,

	PRIMARY KEY("qID"),
	FOREIGN KEY("dID") REFERENCES "uDeck"("dID") ON DELETE CASCADE
);

CREATE TABLE "questionAnswer" (
	"qID" INTEGER,
	"question" TEXT NOT NULL,
	"answer" TEXT NOT NULL,
	
	PRIMARY KEY("qID"),
	FOREIGN KEY("qID") REFERENCES "qDeck"("qID") ON DELETE CASCADE
);

CREATE TABLE "qStat" (
	"qID" INTEGER,
	"easy" INTEGER NOT NULL,
	"medium" INTEGER NOT NULL,
	"hard" INTEGER NOT NULL,
	"attempts" INTEGER NOT NULL,
	
	PRIMARY KEY("qID"),
	FOREIGN KEY("qID") REFERENCES "qDeck"("qID") ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION addQID() RETURNS TRIGGER AS $question_table$
   BEGIN
      INSERT INTO "qStat" VALUES (new."qID", 0, 0, 0, 0);
      RETURN NEW;
   END;
$question_table$ LANGUAGE plpgsql;

CREATE TRIGGER addQID AFTER INSERT ON "questionAnswer"
FOR EACH ROW EXECUTE PROCEDURE addQID();

select * from "uDetails";
select * from "uName";
select * from "uEmail";
select * from "uDeck";
select * from "qDeck";
select * from "questionAnswer";
select * from "qStat";

drop table "uDetails";
drop table "uName";
drop table "uEmail";
drop table "uDeck";
drop table "qDeck";
drop table "questionAnswer";
drop table "qStat";