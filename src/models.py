from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    BigInteger,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class GenderEnum(enum.Enum):
    male = "male"
    female = "female"
    genderless = "genderless"

class RegionEnum(enum.Enum):
    kanto = "kanto"
    johto = "johto"
    hoenn = "hoenn"
    sinnoh = "sinnoh"
    unova = "unova"
    kalos = "kalos"
    alola = "alola"
    galar = "galar"
    hisui = "hisui"
    paldea = "paldea"
    unknown = "unknown"

class Form(Base):
    __tablename__ = "form"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum, name="gender"), nullable=True,)
    region: Mapped[RegionEnum | None] = mapped_column(Enum(RegionEnum, name="region"), nullable=True)

    pokemon: Mapped[list["Pokemon"]] = relationship(back_populates="form")

class Family(Base):
    __tablename__ = "family"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    has_mega: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    pokemon: Mapped[list["Pokemon"]] = relationship(back_populates="family")

class Pokemon(Base):
    __tablename__ = "pokemon"
    __table_args__ = (
        UniqueConstraint("nat_dex_number", "form_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nat_dex_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    form_id: Mapped[int | None] = mapped_column(ForeignKey("form.id"))
    family_id: Mapped[int] = mapped_column(ForeignKey("family.id"), nullable=False)

    form: Mapped["Form"] = relationship(back_populates="pokemon")
    family: Mapped["Family"] = relationship(back_populates="pokemon")
    collection_entries: Mapped[list["CollectionEntry"]] = relationship(back_populates="pokemon")

class Collection(Base):
    __tablename__ = "collection"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    entries: Mapped[list["CollectionEntry"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan"
    )

class CollectionEntry(Base):
    __tablename__ = "collection_entries"
    __table_args__ = (
        UniqueConstraint("collection_id", "pokemon_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collection.id", ondelete="CASCADE"),
        nullable=False
    )
    pokemon_id: Mapped[int] = mapped_column(
        ForeignKey("pokemon.id"),
        nullable=False
    )

    preferred_gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum))
    is_caught: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_mega_hundo_caught: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    collection: Mapped["Collection"] = relationship(back_populates="entries")
    pokemon: Mapped["Pokemon"] = relationship(back_populates="collection_entries")
