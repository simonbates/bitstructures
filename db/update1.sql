CREATE TABLE `substructure_tag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE `substructure_entrytag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `entry_id` integer NOT NULL REFERENCES `substructure_entry` (`id`),
    `tag_id` integer NOT NULL REFERENCES `substructure_tag` (`id`),
    `number` integer NOT NULL
) ENGINE=InnoDB;

ALTER TABLE substructure_entrytag ADD CONSTRAINT UNIQUE (entry_id, number);
