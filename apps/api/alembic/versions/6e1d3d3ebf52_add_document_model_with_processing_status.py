"""add document model with processing status

Revision ID: 6e1d3d3ebf52
Revises: 5d9c2c2dae41
Create Date: 2026-08-05 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6e1d3d3ebf52'
down_revision = '5d9c2c2dae41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the ProcessingStatus enum type in Postgres
    processingstatus = postgresql.ENUM(
        'PENDING', 'PROCESSING', 'SUCCESS', 'FAILED',
        name='processingstatus',
        create_type=True,
    )
    processingstatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_ext', sa.String(10), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('num_chunks', sa.Integer(), nullable=True),
        sa.Column(
            'status',
            sa.Enum('PENDING', 'PROCESSING', 'SUCCESS', 'FAILED',
                    name='processingstatus', create_type=False),
            nullable=False,
            server_default='PENDING',
        ),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('task_id', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    sa.Enum(name='processingstatus').drop(op.get_bind(), checkfirst=True)
