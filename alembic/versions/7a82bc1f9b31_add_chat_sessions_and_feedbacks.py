"""add_chat_sessions_and_feedbacks

Revision ID: 7a82bc1f9b31
Revises: 0d7230a34280
Create Date: 2026-06-20 16:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a82bc1f9b31'
down_revision: Union[str, None] = '0d7230a34280'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_uuid', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_sessions_id'), 'chat_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_chat_sessions_session_uuid'), 'chat_sessions', ['session_uuid'], unique=True)

    # 2. Add session_id column to chat_messages
    with op.batch_alter_table('chat_messages') as batch_op:
        batch_op.add_column(sa.Column('session_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_chat_messages_session_id',
            'chat_sessions',
            ['session_id'], ['id'],
            ondelete='CASCADE'
        )

    # 3. Create chatbot_feedbacks table
    op.create_table(
        'chatbot_feedbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('chat_message_id', sa.Integer(), nullable=False),
        sa.Column('feedback_type', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['chat_message_id'], ['chat_messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'chat_message_id', name='uq_user_message_feedback')
    )
    op.create_index(op.f('ix_chatbot_feedbacks_id'), 'chatbot_feedbacks', ['id'], unique=False)


def downgrade() -> None:
    # 1. Drop chatbot_feedbacks table
    op.drop_index(op.f('ix_chatbot_feedbacks_id'), table_name='chatbot_feedbacks')
    op.drop_table('chatbot_feedbacks')

    # 2. Remove session_id column from chat_messages
    with op.batch_alter_table('chat_messages') as batch_op:
        batch_op.drop_constraint('fk_chat_messages_session_id', type_='foreignkey')
        batch_op.drop_column('session_id')

    # 3. Drop chat_sessions table
    op.drop_index(op.f('ix_chat_sessions_session_uuid'), table_name='chat_sessions')
    op.drop_index(op.f('ix_chat_sessions_id'), table_name='chat_sessions')
    op.drop_table('chat_sessions')
